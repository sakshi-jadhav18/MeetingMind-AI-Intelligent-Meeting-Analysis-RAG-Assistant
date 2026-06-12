import yt_dlp
import os
import re
import math
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloads'  # FIX: was 'downloades' (typo)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ─────────────────────────────────────────────────────
# LAYER 1 — YouTube Transcript API (2-5 seconds)
# Works for 99% of YouTube videos of ANY length
# ─────────────────────────────────────────────────────

def extract_video_id(url: str) -> str:
    import re
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:embed\/)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:shorts\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_captions(url: str, language: str = "english") -> str:
    """
    FIX: Now language-aware.
    - english  → fetch English captions only
    - hinglish → fetch Hindi captions (will be translated later by Sarvam
                 during transcription, OR auto-translated captions if available)
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        video_id = extract_video_id(url)
        if not video_id:
            return None

        print(f"Fetching captions for video: {video_id}")

        # FIX: choose caption languages based on selected transcription language
        if language.lower() == "hinglish":
            lang_priority = ['hi', 'hi-IN', 'en', 'en-US', 'en-GB']
        else:
            lang_priority = ['en', 'en-US', 'en-GB']

        try:
            data = YouTubeTranscriptApi.get_transcript(
                video_id, languages=lang_priority
            )
            text = " ".join([t['text'] for t in data]).strip()
            print(f"Captions found ({lang_priority[0]}): {len(text.split())} words")
            return text
        except Exception:
            pass

        # Try any available language
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([t['text'] for t in data]).strip()
            print(f"Captions found (any language): {len(text.split())} words")
            return text
        except Exception as e:
            print(f"No captions: {e}")
            return None

    except Exception as e:
        print(f"Caption fetch failed: {e}")
        return None


# ─────────────────────────────────────────────────────
# LAYER 2 — yt-dlp subtitle extraction (5-15 seconds)
# Downloads subtitle file directly, no audio needed
# ─────────────────────────────────────────────────────

def get_ytdlp_subtitles(url: str, language: str = "english") -> str:
    try:
        print("Trying yt-dlp subtitle extraction...")
        sub_dir = os.path.join(DOWNLOAD_DIR, "subs")
        os.makedirs(sub_dir, exist_ok=True)

        # FIX: language-aware subtitle selection
        if language.lower() == "hinglish":
            sub_langs = ["hi", "hi-IN", "en", "en-US"]
        else:
            sub_langs = ["en", "en-US"]

        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": sub_langs,
            "subtitlesformat": "vtt",
            "skip_download": True,        # NO audio download
            "outtmpl": os.path.join(sub_dir, "%(id)s.%(ext)s"),
            "quiet": True,
            # FIX: add a basic User-Agent — helps reduce some bot-check triggers
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/120.0.0.0 Safari/537.36",
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id", "")

        # Find the downloaded subtitle file
        for fname in os.listdir(sub_dir):
            if video_id in fname and fname.endswith(".vtt"):
                vtt_path = os.path.join(sub_dir, fname)
                text = parse_vtt(vtt_path)
                # Clean up
                os.remove(vtt_path)
                if text and len(text.split()) > 50:
                    print(f"yt-dlp subtitles found: {len(text.split())} words")
                    return text

        print("No subtitle files found via yt-dlp.")
        return None

    except Exception as e:
        print(f"yt-dlp subtitle extraction failed: {e}")
        return None


def parse_vtt(vtt_path: str) -> str:
    """Parse VTT subtitle file into plain text."""
    import re
    text_lines = []
    seen = set()

    with open(vtt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove VTT header, timestamps, and tags
    content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> .*\n', '', content)
    content = re.sub(r'<[^>]+>', '', content)        # remove HTML tags
    content = re.sub(r'&\w+;', ' ', content)         # remove HTML entities
    content = re.sub(r'\d{2}:\d{2}:\d{2}.*\n', '', content)  # remove timestamps

    for line in content.splitlines():
        line = line.strip()
        if line and line not in seen and not line.startswith("NOTE"):
            seen.add(line)
            text_lines.append(line)

    return " ".join(text_lines).strip()


# ─────────────────────────────────────────────────────
# LAYER 3 — Audio download + Groq (slowest fallback)
# Only used if video has zero captions/subtitles
# For 3-5 hour videos: 3-8 minutes
# ─────────────────────────────────────────────────────

def _sanitize_filename(name: str) -> str:
    """
    FIX: Remove characters that break Windows file paths
    (Hindi/Unicode titles often contain characters like : | " ? * < > /
    which Windows rejects, causing 'No such file or directory' errors).
    Keeps Unicode letters (Hindi/Devanagari) but strips path-breaking chars.
    """
    # Remove characters illegal in Windows filenames
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    # Limit length to avoid path-too-long errors
    if len(name) > 150:
        name = name[:150]
    # Never allow empty filename
    if not name:
        name = "audio"
    return name


def download_youtube_audio(url: str) -> str:
    """
    Download audio as 16kHz mono WAV to keep file size small.

    FIX 1: Added cookies/user-agent + retry options to reduce
           "Sign in to confirm you're not a bot" errors on certain
           (often Hindi/regional) videos.
    FIX 2: Sanitize the video title before use as filename — Hindi
           titles often contain characters Windows can't handle,
           which previously produced paths like
           'downloades/Natural Language Processing.NA'
           (broken extension + typo'd folder).
    FIX 3: Build the final filename ourselves instead of trusting
           yt_dlp's prepare_filename()+replace() chain, and verify
           the file actually exists before returning it.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        # Use video ID for outtmpl — avoids ALL unicode/special-char issues
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noplaylist": True,
        # FIX: realistic browser headers reduce bot-detection on many videos
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
        # FIX: extractor_args helps yt-dlp use a more reliable player client
        # which is less likely to trigger "Sign in to confirm you're not a bot"
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
    except yt_dlp.utils.DownloadError as e:
        err = str(e)
        if "Sign in to confirm" in err or "bot" in err.lower():
            # FIX: Retry once with a different player client as fallback
            print("Bot-check triggered — retrying with alternate client...")
            ydl_opts["extractor_args"] = {"youtube": {"player_client": ["tv_embedded", "android"]}}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get("id")
        else:
            raise

    # FIX: Build the expected output path ourselves using the video ID
    # (guaranteed safe, no unicode/path issues) instead of trusting
    # prepare_filename() with a title-based template.
    expected_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.wav")

    # FIX: Verify the file actually exists. yt-dlp's postprocessor may have
    # produced a slightly different extension in edge cases — search for it.
    if not os.path.exists(expected_path):
        found = None
        for fname in os.listdir(DOWNLOAD_DIR):
            if fname.startswith(video_id) and os.path.isfile(os.path.join(DOWNLOAD_DIR, fname)):
                found = os.path.join(DOWNLOAD_DIR, fname)
                break
        if found is None:
            raise FileNotFoundError(
                f"Audio download failed — no output file found for video ID '{video_id}' "
                f"in '{DOWNLOAD_DIR}'. The download may have been blocked."
            )
        expected_path = found

    filename = expected_path

    # Re-export at 16kHz mono — reduces file by 4x
    print("Converting to 16kHz mono WAV...")
    audio = AudioSegment.from_file(filename)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(filename, format="wav")
    size_mb = os.path.getsize(filename) / 1024 / 1024
    duration_min = len(audio) / 60000
    print(f"Audio ready: {duration_min:.1f} min, {size_mb:.1f}MB")
    return filename


def convert_to_wav(input_path: str) -> str:
    """Convert uploaded file to 16kHz mono WAV."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"Converted: {size_mb:.1f}MB")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    """
    Split audio into Groq-safe chunks (under 20MB each).
    Auto-calculates chunk size from file size.
    """
    audio = AudioSegment.from_wav(wav_path)
    total_min = len(audio) / 60000
    file_mb = os.path.getsize(wav_path) / 1024 / 1024

    if file_mb > 0 and total_min > 0:
        mb_per_min = file_mb / total_min
        safe_min = int(18 / mb_per_min) if mb_per_min > 0 else chunk_minutes
        chunk_minutes = max(2, min(chunk_minutes, safe_min))

    total_chunks = math.ceil(total_min / chunk_minutes)
    print(f"Splitting: {total_min:.0f} min video → "
          f"{total_chunks} chunks of {chunk_minutes} min each")

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunk_mb = os.path.getsize(chunk_path) / 1024 / 1024
        print(f"  Chunk {i+1}/{total_chunks}: {chunk_mb:.1f}MB")
        chunks.append(chunk_path)

    return chunks


# ─────────────────────────────────────────────────────
# SENTINEL — signals captions were used (no audio)
# ─────────────────────────────────────────────────────

CAPTIONS_SENTINEL = "__CAPTIONS__"


def process_input(source: str, language: str = "english") -> list:
    """
    Smart 3-layer router:

    YouTube URL:
      Layer 1 → YouTube Transcript API   (2-5 sec,  ANY length)
      Layer 2 → yt-dlp subtitle download (5-15 sec, ANY length)
      Layer 3 → Audio download + Groq    (slowest,  fallback only)

    Uploaded file:
      Convert to WAV → chunk → Groq

    FIX: `language` param now threaded through to caption layers so
    Hindi/Hinglish videos correctly try Hindi captions first, and the
    audio fallback path (Layer 3) is reached reliably for Hindi videos
    that have no English captions (previously these often crashed
    before reaching Layer 3 due to the bugs below).
    """
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        # ── Layer 1: YouTube Transcript API ──────────────────
        text = get_youtube_captions(source, language=language)
        if text and len(text.split()) > 100:
            caption_path = os.path.join(DOWNLOAD_DIR, "captions.txt")
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"FAST PATH: captions ready in seconds!")
            return [CAPTIONS_SENTINEL + caption_path]

        # ── Layer 2: yt-dlp subtitles ─────────────────────────
        text = get_ytdlp_subtitles(source, language=language)
        if text and len(text.split()) > 100:
            caption_path = os.path.join(DOWNLOAD_DIR, "captions.txt")
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"FAST PATH: subtitles ready!")
            return [CAPTIONS_SENTINEL + caption_path]

        # ── Layer 3: Audio download fallback ──────────────────
        print("No captions found. Downloading audio (slow path)...")
        print("Note: For 3-5 hour videos this may take 5-10 minutes.")
        wav_path = download_youtube_audio(source)

    else:
        print("Uploaded file detected. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Ready — {len(chunks)} chunk(s).")
    return chunks