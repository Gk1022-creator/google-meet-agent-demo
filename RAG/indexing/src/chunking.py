
from __future__ import annotations
from typing import List

def chunk_text(text: str, max_chars: int = 2000, overlap: int = 250) -> List[str]:
    text = text or ""
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + max_chars, n)
        chunks.append(text[i:end])
        if end >= n:
            break
        i = max(0, end - overlap)
    return chunks
