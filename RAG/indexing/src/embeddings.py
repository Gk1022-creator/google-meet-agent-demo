
from __future__ import annotations
from typing import List, Literal, Optional
from dataclasses import dataclass
import requests

@dataclass
class EmbeddingBackend:
    name: Literal["ollama", "sentence_transformers"]
    model: str
    st_model: Optional[str] = None

class Embedder:
    def __init__(self, backend: EmbeddingBackend, ollama_url: str = "http://localhost:11434"):
        self.backend = backend
        self.ollama_url = ollama_url
        self._st = None
        if self.backend.name == "sentence_transformers":
            from sentence_transformers import SentenceTransformer
            model_name = self.backend.st_model or "sentence-transformers/all-MiniLM-L6-v2"
            self._st = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.backend.name == "ollama":
            # Batch through Ollama
            vecs = []
            for t in texts:
                r = requests.post(f"{self.ollama_url}/api/embed", 
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.backend.model,
                    "input": t
                }, timeout=60)
                r.raise_for_status()
                vecs.append(r.json()["embeddings"])
            
            return vecs
        else:
            return self._st.encode(texts, normalize_embeddings=True).tolist()
