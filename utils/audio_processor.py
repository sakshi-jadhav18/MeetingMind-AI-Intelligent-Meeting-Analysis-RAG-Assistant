import yt_dlp
import os
import math
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloades'
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


def get_youtube_captions(url: str) -> str:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        video_id = extract_video_id(url)
        if not video_id:
            return None

        print(f"Fetching captions for video: {video_id}")

        # New API style — works with 0.6.x
        try:
            data = YouTubeTranscriptApi.get_transcript(
                video_id, languages=['en', 'en-US', 'en-GB']
            )
            text = " ".join([t['text'] for t in data]).strip()
            print(f"English captions found: {len(text.split())} words")
            return text
        except Exception:
            pass

        # Try any available language
        try:
            data = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([t['text'] for t in data]).strip()
            print(f"Captions found: {len(text.split())} words")
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

def get_ytdlp_subtitles(url: str) -> str:
    try:
        print("Trying yt-dlp subtitle extraction...")
        sub_dir = os.path.join(DOWNLOAD_DIR, "subs")
        os.makedirs(sub_dir, exist_ok=True)

        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-US"],
            "subtitlesformat": "vtt",
            "skip_download": True,        # NO audio download
            "outtmpl": os.path.join(sub_dir, "%(id)s.%(ext)s"),
            "quiet": True,
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

def download_youtube_audio(url: str) -> str:
    """Download audio as 16kHz mono WAV to keep file size small."""
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = (ydl.prepare_filename(info)
                    .replace(".webm", ".wav")
                    .replace(".m4a", ".wav"))

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


def process_input(source: str) -> list:
    """
    Smart 3-layer router:

    YouTube URL:
      Layer 1 → YouTube Transcript API   (2-5 sec,  ANY length)
      Layer 2 → yt-dlp subtitle download (5-15 sec, ANY length)
      Layer 3 → Audio download + Groq    (slowest,  fallback only)

    Uploaded file:
      Convert to WAV → chunk → Groq
    """
    is_url = source.startswith("http://") or source.startswith("https://")

    if is_url:
        # ── Layer 1: YouTube Transcript API ──────────────────
        text = get_youtube_captions(source)
        if text and len(text.split()) > 100:
            caption_path = os.path.join(DOWNLOAD_DIR, "captions.txt")
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"FAST PATH: captions ready in seconds!")
            return [CAPTIONS_SENTINEL + caption_path]

        # ── Layer 2: yt-dlp subtitles ─────────────────────────
        text = get_ytdlp_subtitles(source)
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