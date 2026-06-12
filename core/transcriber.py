import os
import time
import math
import requests
from pydub import AudioSegment

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
GROQ_API_KEY         = os.getenv("GROQ_API_KEY")
ASSEMBLYAI_API_KEY   = os.getenv("ASSEMBLYAI_API_KEY")
SARVAM_API_KEY       = os.getenv("SARVAM_API_KEY")
SARVAM_STT_URL       = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL         = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")
WHISPER_MODEL        = os.getenv("WHISPER_MODEL", "small")
SARVAM_PIECE_SECONDS = 25
GROQ_MAX_BYTES       = 20 * 1024 * 1024   # 20MB

# Sentinel — set by audio_processor when captions were fetched
CAPTIONS_SENTINEL    = "__CAPTIONS__"

_whisper_model = None


# ---------------------------------------------------------------------------
# ENGINE 1 — AssemblyAI
# Best for uploaded files of ANY length, no chunking needed
# Free: 5 hours/month | Any file size | Most accurate
# ---------------------------------------------------------------------------

def transcribe_assemblyai(file_path: str) -> str:
    """
    Upload file to AssemblyAI and get transcript.
    Handles files of ANY size and length in one API call.
    3 hour video = ~3-4 minutes.
    """
    if not ASSEMBLYAI_API_KEY:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set in .env")

    import assemblyai as aai
    aai.settings.api_key = ASSEMBLYAI_API_KEY

    file_size_mb = os.path.getsize(file_path) / 1024 / 1024
    print(f"Uploading to AssemblyAI ({file_size_mb:.1f}MB)...")
    print("AssemblyAI processes any length file — please wait...")

    transcriber = aai.Transcriber()

    config = aai.TranscriptionConfig(
        speech_model=aai.SpeechModel.best,   # most accurate model
        language_code="en",
        punctuate=True,
        format_text=True,
    )

    transcript = transcriber.transcribe(file_path, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI error: {transcript.error}")

    words = len(transcript.text.split())
    print(f"AssemblyAI done: {words} words transcribed.")
    return transcript.text


# ---------------------------------------------------------------------------
# ENGINE 2 — Groq Whisper API
# Best for YouTube audio chunks (already split to <20MB)
# Free tier, very fast (5-8 sec per chunk)
# ---------------------------------------------------------------------------

def _split_for_groq(chunk_path: str) -> list:
    """Split file into <20MB pieces if needed."""
    if os.path.getsize(chunk_path) <= GROQ_MAX_BYTES:
        return [chunk_path]

    audio      = AudioSegment.from_file(chunk_path)
    total_ms   = len(audio)
    num_pieces = math.ceil(os.path.getsize(chunk_path) / GROQ_MAX_BYTES)
    piece_ms   = math.ceil(total_ms / num_pieces)
    pieces     = []

    for i, start in enumerate(range(0, total_ms, piece_ms)):
        piece      = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_gp_{i}.wav"
        piece.export(piece_path, format="wav",
                     parameters=["-ar", "16000", "-ac", "1"])
        print(f"    Sub-piece {i+1}/{num_pieces}: "
              f"{os.path.getsize(piece_path)/1024/1024:.1f}MB")
        pieces.append(piece_path)

    return pieces


def _groq_send(piece_path: str) -> str:
    """Send one audio file to Groq Whisper with retry."""
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)

    for attempt in range(4):
        try:
            with open(piece_path, "rb") as f:
                result = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=f,
                    response_format="text",
                )
            return result
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "rate" in err:
                wait = 15 * (attempt + 1)
                print(f"    Groq rate limit. Waiting {wait}s "
                      f"(attempt {attempt+1}/4)...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("Groq Whisper rate limit: max retries exceeded.")


def transcribe_chunk_groq(chunk_path: str) -> str:
    """Transcribe one chunk via Groq. Auto-splits if over 20MB."""
    pieces   = _split_for_groq(chunk_path)
    is_split = pieces != [chunk_path]
    text     = ""

    try:
        for i, piece in enumerate(pieces):
            size_mb = os.path.getsize(piece) / 1024 / 1024
            label   = f" piece {i+1}/{len(pieces)}" if len(pieces) > 1 else ""
            print(f"  Groq transcribing{label} ({size_mb:.1f}MB)...")
            text += _groq_send(piece) + " "
    finally:
        if is_split:
            for p in pieces:
                if os.path.exists(p):
                    os.remove(p)

    return text.strip()


# ---------------------------------------------------------------------------
# ENGINE 3 — Sarvam AI
# For Hinglish → translates to English while transcribing
# ---------------------------------------------------------------------------

def _send_to_sarvam(piece_path: str, max_retries: int = 5) -> str:
    headers = {"api-subscription-key": SARVAM_API_KEY}

    for attempt in range(max_retries):
        with open(piece_path, "rb") as f:
            files    = {"file": (os.path.basename(piece_path), f, "audio/wav")}
            data     = {"model": SARVAM_MODEL, "with_diarization": "false"}
            response = requests.post(
                SARVAM_STT_URL, headers=headers,
                files=files, data=data, timeout=120,
            )

        if response.status_code == 429:
            wait = 15 * (attempt + 1)
            print(f"  Sarvam rate limit. Waiting {wait}s "
                  f"(retry {attempt+1}/{max_retries})...")
            time.sleep(wait)
            continue

        if not response.ok:
            print(f"Sarvam error {response.status_code}: {response.text}")
            response.raise_for_status()

        time.sleep(3)
        return response.json().get("transcript", "")

    raise RuntimeError(f"Sarvam rate limit exceeded after {max_retries} retries.")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    """Split into <=25s pieces and send each to Sarvam."""
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in .env")

    audio        = AudioSegment.from_wav(chunk_path)
    piece_ms     = SARVAM_PIECE_SECONDS * 1000
    total_pieces = math.ceil(len(audio) / piece_ms)
    full_text    = ""

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece      = audio[start: start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")
        try:
            print(f"  Sarvam piece {i+1}/{total_pieces}...")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


# ---------------------------------------------------------------------------
# ENGINE 4 — Local Whisper (fallback if no API keys)
# ---------------------------------------------------------------------------

def _load_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print(f"Loading Whisper model: {WHISPER_MODEL}...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded.")
    return _whisper_model


def transcribe_chunk_whisper(chunk_path: str) -> str:
    model  = _load_whisper()
    result = model.transcribe(chunk_path, task="transcribe")
    return result["text"]


# ---------------------------------------------------------------------------
# MAIN ENTRY — transcribe_all
# Called by app.py processing screen
# ---------------------------------------------------------------------------

def transcribe_all(chunks: list, language: str = "english") -> str:
    """
    Smart routing:

    FAST PATH   — captions already fetched by audio_processor
                  reads text file → milliseconds

    UPLOADED    — AssemblyAI handles ANY file size/length in one call
                  no chunking, most accurate, 3hr video = 3-4 min

    YOUTUBE     — Groq Whisper on pre-chunked audio (parallel)
                  fast, handles any length

    HINGLISH    — Sarvam AI (translates to English)

    FALLBACK    — Local Whisper if no API keys set
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ── FAST PATH: pre-fetched captions ──────────────────────────────────
    if len(chunks) == 1 and chunks[0].startswith(CAPTIONS_SENTINEL):
        caption_path = chunks[0][len(CAPTIONS_SENTINEL):]
        print(f"Reading pre-fetched captions...")
        with open(caption_path, "r", encoding="utf-8") as f:
            transcript = f.read()
        print(f"Transcript ready: {len(transcript.split())} words")
        return transcript.strip()

    # ── HINGLISH: Sarvam AI ───────────────────────────────────────────────
    if language.lower() == "hinglish":
        print(f"Engine: Sarvam AI | Chunks: {len(chunks)}")
        full = ""
        for i, chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}...")
            full += transcribe_chunk_sarvam(chunk) + " "
        print("Transcription complete.")
        return full.strip()

    # ── UPLOADED FILE: AssemblyAI (single file, any size) ─────────────────
    # Detect uploaded file: only 1 chunk and file is large or no _chunk_ in name
    is_uploaded = (
        len(chunks) == 1 and
        "_chunk_" not in chunks[0] and
        ASSEMBLYAI_API_KEY
    )

    if is_uploaded:
        print("Engine: AssemblyAI (uploaded file — any length supported)")
        return transcribe_assemblyai(chunks[0])

    # ── YOUTUBE AUDIO: Groq parallel chunks ───────────────────────────────
    if GROQ_API_KEY:
        print(f"Engine: Groq Whisper (cloud) | Chunks: {len(chunks)}")

        if len(chunks) == 1:
            return transcribe_chunk_groq(chunks[0])

        # Run up to 3 chunks in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_map = {
                executor.submit(transcribe_chunk_groq, c): i
                for i, c in enumerate(chunks)
            }
            for future in as_completed(future_map):
                idx          = future_map[future]
                results[idx] = future.result()
                print(f"  Chunk {idx+1}/{len(chunks)} complete")

        return " ".join(results[i] for i in range(len(chunks))).strip()

    # ── FALLBACK: local Whisper ────────────────────────────────────────────
    print(f"Engine: Whisper local ({WHISPER_MODEL}) | Chunks: {len(chunks)}")
    full = ""
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        full += transcribe_chunk_whisper(chunk) + " "
    print("Transcription complete.")
    return full.strip()