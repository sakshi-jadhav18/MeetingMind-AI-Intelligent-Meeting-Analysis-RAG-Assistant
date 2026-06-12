# MeetMind AI — Intelligent Meeting Analysis & RAG Assistant

MeetMind AI is an AI-powered meeting assistant that transcribes audio recordings, generates concise summaries, and lets you ask questions about your meetings using a Retrieval-Augmented Generation (RAG) chatbot.

## Features

- **Audio Transcription** — Converts meeting recordings into text using Whisper.
- **AI Summarization** — Generates concise meeting summaries and key points using LangChain.
- **RAG-based Q&A** — Ask natural language questions about past meetings, powered by ChromaDB vector search.
- **Interactive UI** — Simple Streamlit interface for uploading recordings, viewing summaries, and chatting with your meeting data.

## Tech Stack

- **Python**
- **Whisper** — Speech-to-text transcription
- **LangChain** — Summarization and RAG pipeline orchestration
- **ChromaDB** — Vector database for embeddings storage and retrieval
- **Sentence Transformers** — Embedding generation (all-MiniLM-L6-v2)
- **Streamlit** — Web UI
- **Groq / Gemini API** — LLM inference

## Project Structure

```
MeetMind-AI/
├── core/
│   ├── extractor.py        # Extracts text/audio content
│   ├── transcriber.py       # Whisper-based transcription
│   ├── sammarize.py          # Meeting summarization logic
│   ├── rag_engine.py        # RAG pipeline and chatbot logic
│   └── vector_store.py      # ChromaDB vector storage management
├── utils/
│   └── audio_processor.py   # Audio preprocessing utilities
├── app.py                   # Streamlit application entry point
├── main.py                  # Core pipeline runner
├── requirements.txt         # Python dependencies

```

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/sakshi-jadhav18/MeetingMind-AI-Intelligent-Meeting-Analysis-RAG-Assistant.git
cd MeetingMind-AI-Intelligent-Meeting-Analysis-RAG-Assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root with your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
GCP_API_KEY=your_gcp_api_key_here
```

> **Note:** Never commit your `.env` file. It's already excluded via `.gitignore`.

### 5. Run the application

```bash
streamlit run app.py
```

## First-Run Notes

- On first run, the app will automatically download the `all-MiniLM-L6-v2` sentence-transformer model into a local `.embeddings_cache/` folder (~90 MB). This requires an internet connection.
- A `vector_db/` folder will be created automatically by ChromaDB to store meeting embeddings locally.
- Both `.embeddings_cache/` and `vector_db/` are gitignored and regenerate automatically — no manual setup needed.

## How It Works

1. **Upload** a meeting audio recording.
2. **Transcribe** — Whisper converts speech to text.
3. **Summarize** — LangChain generates a structured summary with key points and action items.
4. **Store** — Transcript embeddings are stored in ChromaDB.
5. **Ask** — Query past meetings via the RAG chatbot for instant answers.

## Future Improvements

- Speaker diarization for multi-participant meetings
- Export summaries as PDF/Word documents
- Support for live meeting transcription

## Author

**Sakshi Jadhav**
[Portfolio](https://sakshi-portfolio-eozi.vercel.app/)
