# 🎙️ MeetMind AI — Intelligent Meeting Analysis & RAG Assistant

> Transform any meeting recording or YouTube video into structured insights — summaries, action items, decisions, and an AI you can chat with.

---

## ✨ What MeetMind AI Does

MeetMind AI takes a YouTube URL or uploaded audio/video file and automatically:

1. **Transcribes** the speech to text (English & Hinglish supported)
2. **Generates** a professional meeting title
3. **Summarizes** key topics and outcomes in bullet points
4. **Extracts** action items, key decisions, and open questions
5. **Builds** a RAG (Retrieval-Augmented Generation) knowledge base from the transcript
6. **Lets you chat** with your meeting using natural language Q&A

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🎥 YouTube URL input | Paste any YouTube link — captions fetched in seconds |
| 📁 File upload | Upload MP3, MP4, WAV, M4A, WEBM files |
| 🌐 Multilingual | English and Hinglish → English transcription |
| ⚡ Fast path | Uses YouTube captions when available (2-5 seconds) |
| 🤖 AI summarization | Bullet-point summary via Groq/Mistral/Gemini |
| ✅ Action items | Automatically extracted with owner and deadline |
| 🔑 Key decisions | All major decisions listed |
| ❓ Open questions | Unresolved topics flagged |
| 💬 RAG chatbot | Ask anything about your meeting |
| 📄 Export | Download results as TXT or PDF |
| 🎨 Premium UI | Clean light-theme Streamlit interface |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit |
| **Audio download** | yt-dlp |
| **Audio processing** | pydub |
| **Transcription (English)** | Groq Whisper API |
| **Transcription (Hinglish)** | Sarvam AI (saaras:v2.5) |
| **Local transcription** | OpenAI Whisper (fallback) |
| **Summarization / Extraction** | Groq LLaMA, Mistral, Gemini |
| **Embeddings** | HuggingFace sentence-transformers (all-MiniLM-L6-v2) |
| **Vector database** | ChromaDB |
| **RAG pipeline** | LangChain |

---

## 📁 Project Structure

```
MeetMind-AI/
├── core/
│   ├── transcriber.py      # Multi-engine transcription (Groq, Sarvam, Whisper)
│   ├── sammarize.py        # Title generation + summarization (Groq/Mistral/Gemini)
│   ├── extractor.py        # Action items, decisions, questions extraction
│   └── rag_engine.py       # ChromaDB vector store + RAG chat
├── utils/
│   └── audio_processor.py  # YouTube download, audio chunking, caption fetching
├── app.py                  # Streamlit UI (main entry point)
├── main.py                 # CLI pipeline runner
├── requirements.txt        # Python dependencies
├── .env                    # API keys (never committed)
└── .streamlit/
    └── config.toml         # Streamlit server config (disables file watcher noise)
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/sakshi-jadhav18/MeetingMind-AI-Intelligent-Meeting-Analysis-RAG-Assistant.git
cd MeetingMind-AI-Intelligent-Meeting-Analysis-RAG-Assistant
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `ffmpeg` must also be installed on your system.
> - Windows: `winget install ffmpeg`
> - macOS: `brew install ffmpeg`
> - Ubuntu: `sudo apt install ffmpeg`

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
MISTRAL_API_KEY=your_mistral_api_key
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
SARVAM_API_KEY=your_sarvam_api_key
SARVAM_STT_MODEL=saaras:v2.5
WHISPER_MODEL=small
```

> ⚠️ Never commit your `.env` file. It is already excluded via `.gitignore`.

**Get free API keys:**
| API | Free Tier | Link |
|---|---|---|
| Groq | 100 req/day | [console.groq.com](https://console.groq.com) |
| Mistral | Generous free tier | [console.mistral.ai](https://console.mistral.ai) |
| Gemini | 60 req/min | [aistudio.google.com](https://aistudio.google.com) |
| Sarvam | Free tier | [sarvam.ai](https://sarvam.ai) |

### 5. Run the application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 📖 How It Works (Step by Step)

```
YouTube URL / Audio File
        │
        ▼
┌─────────────────────────────────────────┐
│         LAYER 1 — YouTube Captions      │  ← 2-5 seconds (fastest)
│   YouTubeTranscriptApi.get_transcript() │
└─────────────────────────────────────────┘
        │ (if no captions)
        ▼
┌─────────────────────────────────────────┐
│         LAYER 2 — yt-dlp Subtitles      │  ← 5-15 seconds
│   Downloads .vtt subtitle file          │
└─────────────────────────────────────────┘
        │ (if no subtitles)
        ▼
┌─────────────────────────────────────────┐
│         LAYER 3 — Audio Download        │  ← 1-5 minutes
│   yt-dlp + Groq Whisper transcription   │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│           LLM PROCESSING                │
│  Title → Summary → Actions →            │
│  Decisions → Questions                  │
│  (Groq → Mistral → Gemini fallback)     │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│           RAG PIPELINE                  │
│  ChromaDB vector store built            │
│  HuggingFace embeddings generated       │
└─────────────────────────────────────────┘
        │
        ▼
    Results shown in browser
    (Summary, Actions, Decisions, Chat)
```

---

## 🌐 Language Support

| Input Language | Transcription Engine | Output Language |
|---|---|---|
| English | Groq Whisper | English |
| Hindi / Hinglish | Sarvam AI (saaras:v2.5) | English |

---

## ⏱️ Expected Processing Times

| Video Length | With Captions | Without Captions |
|---|---|---|
| 15 seconds | ~10 sec | ~45 sec |
| 5 minutes | ~15 sec | ~1-2 min |
| 30 minutes | ~20 sec | ~3-5 min |
| 1 hour | ~25 sec | ~5-8 min |
| 3 hours | ~30 sec | ~15-20 min |

---

## 🖥️ Screenshots

### Home Screen
<img width="1912" height="1011" alt="image" src="https://github.com/user-attachments/assets/23e793d9-400f-49ba-a975-6de58cf23c58" />

### Processing Screen
<img width="1917" height="1017" alt="image" src="https://github.com/user-attachments/assets/5cb095a6-c814-4fbd-8873-32b39d0f9168" />


### Results Screen
<img width="1918" height="1012" alt="image" src="https://github.com/user-attachments/assets/4f60e0aa-0784-401e-b62d-9ea32fc2bae9" />


---

## 👩‍💻 Author

**Sakshi Jadhav**
B.Sc. Artificial Intelligence

---
