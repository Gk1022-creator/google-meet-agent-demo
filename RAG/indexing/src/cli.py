
from __future__ import annotations
import click, os, sys, math
from typing import List, Dict, Any
from tqdm import tqdm
from qdrant_client import QdrantClient
from .settings import load_settings
from .chunking import chunk_text
from .embeddings import Embedder, EmbeddingBackend
from .indexer import ensure_collection, upsert_points
from .loaders.mised_loader import load_mised_segments
from .loaders.docs_loader import iter_docs

def _make_embedder(cfg):
    name = cfg.embeddings.backend
    if name not in ("ollama","sentence_transformers"):
        raise SystemExit("embeddings.backend must be 'ollama' or 'sentence_transformers'")
    backend = EmbeddingBackend(name=name, model=cfg.embeddings.model, st_model=cfg.embeddings.st_model)
    return Embedder(backend)

@click.group()
def cli():
    pass

@cli.command()
def show_config():
    cfg = load_settings()
    click.echo(cfg.model_dump_json(indent=2))

@cli.command()
@click.option("--vector-size", default=768, show_default=True, help="Embedding dimension (768 for nomic-embed-text; 384 for MiniLM)")
def create_collection(vector_size: int):
    cfg = load_settings()
    client = QdrantClient(url=cfg.qdrant.url, api_key=cfg.qdrant.api_key)
    ensure_collection(client, cfg.qdrant.collection, vector_size, distance="Cosine")
    click.secho(f"Ensured collection '{cfg.qdrant.collection}' (size={vector_size})", fg="green")

def _pipeline(items: List[Dict[str,Any]]):
    cfg = load_settings()
    embedder = _make_embedder(cfg)
    client = QdrantClient(url=cfg.qdrant.url, api_key=cfg.qdrant.api_key)

    # Detect vector size (simple heuristic)
    vec_size = 768 if cfg.embeddings.backend == "ollama" else (384 if "MiniLM" in cfg.embeddings.st_model else 768)
    ensure_collection(client, cfg.qdrant.collection, vec_size, distance="Cosine")

    payloads: List[Dict[str,Any]] = []
    texts: List[str] = []
    ids: List[str] = []

    for it in items:
        chunks = chunk_text(it["text"], cfg.chunking.max_chars, cfg.chunking.overlap)
        for idx, ch in enumerate(chunks):
            cid = f"{it['doc_id']}#{idx}"
            payloads.append({
                "chunk_id": cid,
                "doc_id": it["doc_id"],
                "source": it.get("source"),
                "origin_id": it.get("origin_id"),
                "title": it.get("title"),
                "speaker": it.get("speaker"),
                "timestamp": it.get("timestamp"),
                "text": ch
            })
            texts.append(ch)
            ids.append(cid)

    if not payloads:
        click.secho("No text to index.", fg="yellow")
        return

    # Embed in batches
    B = 64
    vectors: List[List[float]] = []
    for i in tqdm(range(0, len(texts), B), desc="Embedding"):
        batch = texts[i:i+B]
        vecs = embedder.embed(batch)
        vectors.extend(vecs)

    # Upsert in batches
    U = 256
    for i in tqdm(range(0, len(vectors), U), desc="Upserting"):
        upsert_points(client, cfg.qdrant.collection, vectors[i:i+U], payloads[i:i+U], ids[i:i+U])

    click.secho(f"Indexed {len(vectors)} chunks into '{cfg.qdrant.collection}'", fg="green")

@cli.command()
@click.option("--jsonl", required=True, help="Path or URL to MISeD JSONL")
def ingest_mised(jsonl: str):
    items = list(load_mised_segments(jsonl))
    click.secho(f"Loaded {len(items)} MISeD segments", fg="cyan")
    _pipeline(items)

@cli.command()
@click.option("--path", required=True, type=click.Path(exists=True, file_okay=False), help="Folder containing PDFs/DOCX")
def ingest_docs(path: str):
    items = list(iter_docs(path))
    click.secho(f"Loaded {len(items)} documents", fg="cyan")
    _pipeline(items)

@cli.command()
@click.option("--query", required=True, help="Search query to embed and use against Qdrant")
def search(query: str):
    cfg = load_settings()
    embedder = _make_embedder(cfg)
    client = QdrantClient(url=cfg.qdrant.url, api_key=cfg.qdrant.api_key)
    qvec = embedder.embed([query])[0]
    res = client.search(collection_name=cfg.qdrant.collection, query_vector=qvec, limit=5, with_payload=True)
    for hit in res:
        score = hit.score
        payload = hit.payload or {}
        title = payload.get("title")
        text = (payload.get("text") or "")[:160].replace("\n"," ")
        print(f"[{score:.3f}] {title} :: {text}")

if __name__ == "__main__":
    cli()
