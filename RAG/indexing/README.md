
# Meeting RAG – Workflow A (Python)

Ingest meeting data (MISeD JSONL, PDFs, DOCX, emails) → chunk → embed (Ollama or Sentence-Transformers) → index in Qdrant.

## Quick start

1) Python 3.10+ recommended
2) `pip install -r requirements.txt`
3) Ensure **Qdrant** and **Ollama** are running (or use sentence-transformers fallback):
   - Qdrant: `docker run -p 6333:6333 qdrant/qdrant:latest`
   - Ollama: `docker run -d -p 11434:11434 --name ollama ollama/ollama` then `docker exec -it ollama ollama pull nomic-embed-text`
4) Configure `config.yaml` (or rely on defaults).
5) Create collection:  
   `python -m src.cli create-collection`
6) Ingest MISeD JSONL:  
   `python -m src.cli ingest-mised --jsonl <path or URL>`
7) Ingest documents (folder of PDFs/DOCX):  
   `python -m src.cli ingest-docs --path ./docs`
8) Test search (basic semantic search):  
   `python -m src.cli search --query "forced alignment of schedules"`

## Config
See `config.yaml` for:
- Qdrant URL/collection
- Embedding backend (`ollama` or `sentence_transformers`)
- Chunk sizes, overlaps
- Optional filters

## Structure
- `src/settings.py` – config model
- `src/chunking.py` – splitter with overlap
- `src/embeddings.py` – Ollama + Sentence-Transformers
- `src/indexer.py` – Qdrant helpers
- `src/loaders/mised_loader.py` – parse MISeD JSONL
- `src/loaders/docs_loader.py` – parse PDFs/DOCX (PyMuPDF + python-docx)
- `src/loaders/email_loader.py` – stub with Gmail API pointers
- `src/cli.py` – CLI entry points

