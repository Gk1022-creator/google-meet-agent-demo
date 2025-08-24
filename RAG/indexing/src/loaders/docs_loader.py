
from __future__ import annotations
from typing import Generator, Dict, Any
import os, time
import fitz  # PyMuPDF
from docx import Document

def _read_pdf(path: str) -> str:
    text_parts = []
    with fitz.open(path) as doc:
        for page in doc:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()

def _read_docx(path: str) -> str:
    d = Document(path)
    return "\n".join(p.text for p in d.paragraphs).strip()

def iter_docs(root: str) -> Generator[Dict[str, Any], None, None]:
    now = int(time.time()*1000)
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn.lower())[1]
            try:
                if ext == ".pdf":
                    text = _read_pdf(path)
                elif ext in (".docx", ):
                    text = _read_docx(path)
                else:
                    continue
            except Exception:
                continue
            if not text:
                continue
            origin_id = os.path.relpath(path, root).replace("\\","/")
            yield {
                "doc_id": f"{origin_id}",
                "source": "drive",
                "origin_id": origin_id,
                "title": fn,
                "speaker": None,
                "timestamp": now,
                "text": text
            }
