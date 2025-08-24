
from __future__ import annotations
from typing import Iterable, Dict, Any, Generator, Optional
import json, os, requests, time


import re

def is_useless_chunk(text: str) -> bool:
    """
    Mark as useless if chunk only contains:
    - punctuation (. , - etc.)
    - 1 short filler word like "ah", "oh", "hmm", "alright"
    """
    # Remove prefix
    t = re.sub(r"^text embedded\s*:\s*", "", text).strip()

    # Empty or only dots/dashes/commas
    if not t or re.fullmatch(r"[.,\- ]+", t):
        return True

    # Very short (<=2 words) and looks like filler
    filler_words = {"ah", "oh", "hmm", "mm", "alright", "bye", "yeah", "okay", "ok", "definitely"}
    words = re.findall(r"\b\w+\b", t.lower())
    if len(words) <= 2 and all(w in filler_words for w in words):
        return True

    return False



# Define useless/filler words or phrases
USELESS_PATTERNS = [
    r"\bmm hmm\b",
    r"\bhmm\b",
    r"\buh\b",
    r"\bum\b",
    r"\buh huh\b",
    r"\byeah\b",
    r"\bokay\b",
    r"\bok\b",
    r"\bbye\b",
    r"\bsee you\b",
    r"\bthanks\b",
    r"\bthank you\b",
]

# Combine into one regex pattern (case-insensitive)
USELESS_REGEX = re.compile("|".join(USELESS_PATTERNS), re.IGNORECASE)

def clean_text(text: str) -> str:
    """
    Removes useless filler words/phrases from a text.
    """
    cleaned = USELESS_REGEX.sub("", text)      # remove filler words
    cleaned = re.sub(r"\s+", " ", cleaned)     # normalize spaces
    return cleaned.strip()

def _iter_jsonl_lines(path_or_url: str) -> Iterable[str]:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        r = requests.get(path_or_url, timeout=120)
        r.raise_for_status()
        for line in r.text.splitlines():
            if line.strip():
                yield line
    else:
        with open(path_or_url, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield line

def load_mised_segments(path_or_url: str) -> Generator[Dict[str, Any], None, None]:
    now = int(time.time()*1000)
    for line in _iter_jsonl_lines(path_or_url):
        try:
            obj = json.loads(line)
        except Exception:
            continue
        meeting = obj.get("meeting", {})
        mid = meeting.get("meetingId") or obj.get("dialogId") or "unknown"
        segs = meeting.get("transcriptSegments") or []
        for s in segs:
            speaker = s.get("speakerName")
            text = s.get("text","").strip()

            text = clean_text(text)
            if not text or is_useless_chunk(text):
                continue
            
            print(f"text embedded : {text}")

 
            yield {
                "doc_id": f"{mid}-{speaker or 'unknown'}",
                "source": "mised",
                "origin_id": mid,
                "title": f"{mid}",
                "speaker": speaker,
                "timestamp": now,
                "text": text
            }
        # Optionally emit a meeting-level record here if needed
