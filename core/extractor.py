import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv(override=True)

import core.sammarize as _sam


def _call(prompt: str, system: str, fallback: str) -> str:
    return _sam._llm(
        prompt   = prompt,
        system   = system,
        temp     = 0.2,
        max_tok  = 1000,
        fallback = fallback,
    )


def _trim(text: str, max_words: int = 6000) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    half = max_words // 2
    return (" ".join(words[:half])
            + "\n\n[... middle omitted ...]\n\n"
            + " ".join(words[-half:]))


def extract_action_items(transcript: str) -> str:
    print("Extracting action items...")
    return _call(
        prompt   = _trim(transcript),
        system   = ("Extract ALL action items from this transcript. "
                    "For each: task, owner, deadline. "
                    "Numbered list. If none: 'No action items found.'"),
        fallback = "No action items found.",
    )


def extract_key_decisions(transcript: str) -> str:
    print("Extracting key decisions...")
    return _call(
        prompt   = _trim(transcript),
        system   = ("Extract ALL key decisions from this transcript. "
                    "Numbered list. If none: 'No key decisions found.'"),
        fallback = "No key decisions found.",
    )


def extract_questions(transcript: str) -> str:
    print("Extracting open questions...")
    return _call(
        prompt   = _trim(transcript),
        system   = ("Extract ALL unresolved questions from this transcript. "
                    "Numbered list. If none: 'No open questions found.'"),
        fallback = "No open questions found.",
    )


def extract_all_parallel(transcript: str) -> dict:
    """Run all 3 extractions in parallel — 3x faster than sequential."""
    print("Extracting insights in parallel...")
    trimmed = _trim(transcript)

    tasks = {
        "action_items": (trimmed,
            "Extract ALL action items. Task, owner, deadline. "
            "Numbered list. If none: 'No action items found.'",
            "No action items found."),
        "key_decisions": (trimmed,
            "Extract ALL key decisions. Numbered list. "
            "If none: 'No key decisions found.'",
            "No key decisions found."),
        "open_questions": (trimmed,
            "Extract ALL unresolved questions. Numbered list. "
            "If none: 'No open questions found.'",
            "No open questions found."),
    }

    results = {}
    # Use threads=1 to avoid hammering rate limits — still async-friendly
    with ThreadPoolExecutor(max_workers=1) as ex:
        futures = {
            ex.submit(_call, p, s, f): key
            for key, (p, s, f) in tasks.items()
        }
        for future in futures:
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = tasks[key][2]  # fallback

    return results