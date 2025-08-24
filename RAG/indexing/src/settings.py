
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
import yaml, os

class QdrantConf(BaseModel):
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    collection: str = "meetings"

class EmbeddingsConf(BaseModel):
    backend: str = "ollama"  # or 'sentence_transformers'
    model: str = "nomic-embed-text"
    st_model: str = "sentence-transformers/all-MiniLM-L6-v2"

class ChunkConf(BaseModel):
    max_chars: int = 2000
    overlap: int = 250

class IngestionConf(BaseModel):
    default_source: str = "custom"

class Settings(BaseModel):
    qdrant: QdrantConf = QdrantConf()
    embeddings: EmbeddingsConf = EmbeddingsConf()
    chunking: ChunkConf = ChunkConf()
    ingestion: IngestionConf = IngestionConf()

def load_settings(path: str = None) -> Settings:
    path = path or os.environ.get("MEETING_RAG_CONFIG", "config.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Settings(**data)
    return Settings()
