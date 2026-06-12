"""
sammarize.py — Optimized LLM layer
Primary: Mistral API (fast, generous free tier)
Fallback: Gemini (only if Mistral fails)
"""
import os
import time
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv(override=True)

# ── Clean keys (strip spaces/quotes from .env values) ─────────────────────
def _clean(v):
    return v.strip().strip('"').strip("'").strip() if v else ""

MISTRAL_API_KEY = _clean(os.getenv("MISTRAL_API_KEY", ""))
GEMINI_API_KEY  = _clean(os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", ""))

PRIMARY = "mistral" if MISTRAL_API_KEY else "gemini"
print(f"  [LLM] primary={PRIMARY}  mistral_key={'YES' if MISTRAL_API_KEY else 'NO'}  gemini_key={'YES' if GEMINI_API_KEY else 'NO'}")


# ── Mistral call (handles both old and new SDK versions) ──────────────────
def _mistral_call(prompt: str, system: str, temp: float, max_tok: int) -> str:
    """Supports mistralai>=1.0 (new SDK) and mistralai<1.0 (old SDK)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(3):
        try:
            # ── Try new SDK (mistralai >= 1.0) ──────────────────────────
            try:
                from mistralai import Mistral
                client = Mistral(api_key=MISTRAL_API_KEY)
                resp = client.chat.complete(
                    model="mistral-small-latest",
                    messages=messages,
                    temperature=temp,
                    max_tokens=max_tok,
                )
                return resp.choices[0].message.content.strip()
            except ImportError:
                pass

            # ── Try old SDK (mistralai < 1.0) ───────────────────────────
            try:
                from mistralai.client import MistralClient
                from mistralai.models.chat_completion import ChatMessage
                client = MistralClient(api_key=MISTRAL_API_KEY)
                msgs = [ChatMessage(role=m["role"], content=m["content"])
                        for m in messages]
                resp = client.chat(
                    model="mistral-small-latest",
                    messages=msgs,
                    temperature=temp,
                    max_tokens=max_tok,
                )
                return resp.choices[0].message.content.strip()
            except ImportError:
                pass

            # ── Try requests directly (no SDK needed) ───────────────────
            import requests, json
            r = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": max_tok,
                },
                timeout=60,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

        except Exception as exc:
            err = str(exc).lower()
            if any(k in err for k in ["429", "rate", "quota", "limit", "too many"]):
                wait = 20 * (attempt + 1)
                print(f"  [Mistral] rate limit — waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                raise

    raise RuntimeError("Mistral: max retries exceeded")


# ── Gemini call (fallback only) ────────────────────────────────────────────
_gemini_last = 0.0

def _gemini_call(prompt: str, system: str, temp: float, max_tok: int) -> str:
    global _gemini_last
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-8b",
        system_instruction=system or None,
    )
    cfg = genai.GenerationConfig(temperature=temp, max_output_tokens=max_tok)

    for attempt in range(2):  # Only 2 retries — don't waste minutes
        elapsed = time.time() - _gemini_last
        if elapsed < 6:
            time.sleep(6 - elapsed)
        try:
            _gemini_last = time.time()
            resp = model.generate_content(prompt, generation_config=cfg)
            return resp.text.strip()
        except Exception as exc:
            err = str(exc).lower()
            if any(k in err for k in ["429", "quota", "rate", "exhausted"]):
                wait = 30 * (attempt + 1)
                print(f"  [Gemini] quota — waiting {wait}s (attempt {attempt+1}/2)...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini: max retries exceeded")


# ── Groq LLM call (second fallback — fast and free) ───────────────────────
GROQ_API_KEY = _clean(os.getenv("GROQ_API_KEY", ""))

def _groq_call(prompt: str, system: str, temp: float, max_tok: int) -> str:
    import requests
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(3):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama3-8b-8192",
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": max_tok,
                },
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as exc:
            err = str(exc).lower()
            if any(k in err for k in ["429", "rate", "quota", "limit"]):
                wait = 15 * (attempt + 1)
                print(f"  [Groq] rate limit — waiting {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Groq: max retries exceeded")


# ── Unified LLM entry point ────────────────────────────────────────────────
def _llm(prompt: str, system: str = "", temp: float = 0.3,
         max_tok: int = 1500, fallback: str = "") -> str:

    order = []
    if MISTRAL_API_KEY:
        order.append(("Mistral", _mistral_call))
    if GROQ_API_KEY:
        order.append(("Groq",    _groq_call))
    if GEMINI_API_KEY:
        order.append(("Gemini",  _gemini_call))

    if not order:
        print("  [LLM] No API keys found! Check your .env file.")
        return fallback

    for name, fn in order:
        try:
            print(f"  [LLM] trying {name}...")
            result = fn(prompt, system, temp, max_tok)
            print(f"  [LLM] {name} ✓")
            return result
        except Exception as e:
            print(f"  [LLM] {name} failed: {e}")
            continue

    print("  [LLM] all providers failed — returning fallback")
    return fallback


# ── Truncate helper ────────────────────────────────────────────────────────
def truncate(text: str, max_words: int = 6000) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    half = max_words // 2
    print(f"  [LLM] transcript {len(words)} words → trimmed to {max_words}")
    return (" ".join(words[:half])
            + "\n\n[... middle omitted ...]\n\n"
            + " ".join(words[-half:]))


# ── Public functions ───────────────────────────────────────────────────────
def generate_title(transcript: str) -> str:
    print("Generating title...")
    t0 = time.time()
    result = _llm(
        prompt   = transcript[:1500],
        system   = ("Generate a short professional title in max 8 words. "
                    "Return ONLY the title. No quotes. No period."),
        temp     = 0.2,
        max_tok  = 30,
        fallback = "Meeting Summary",
    ).strip().strip('"').strip("'")
    print(f"  Title done in {time.time()-t0:.1f}s")
    return result


def summarize(transcript: str) -> str:
    word_count = len(transcript.split())
    print(f"Summarizing ({word_count} words)...")
    t0 = time.time()
    result = _llm(
        prompt   = truncate(transcript),
        system   = ("You are an expert meeting summarizer. "
                    "Summarize in clear bullet points. "
                    "Cover all key topics, decisions, and outcomes."),
        temp     = 0.3,
        max_tok  = 1500,
        fallback = "Summary could not be generated — please try again.",
    )
    print(f"  Summary done in {time.time()-t0:.1f}s")
    return result


# ── Backward-compat alias used by extractor.py ────────────────────────────
def _rate_limited_call(prompt, system, temp, max_tok, fallback):
    return _llm(prompt, system, temp, max_tok, fallback)
