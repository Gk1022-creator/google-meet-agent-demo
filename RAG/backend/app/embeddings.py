import requests
import os
from typing import List
from .config import settings

class OllamaEmbedder:
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Call Ollama API for embeddings"""
        vectors = []
        for t in texts:
            r = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": t},
                timeout=120
            )
            r.raise_for_status()
            data = r.json()
            vectors.append(data["embedding"])
        return vectors


# ✅ Add OpenAI Embedder here
class OpenAIEmbedder:
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        import openai
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=self.api_key)

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Call OpenAI API for embeddings"""
        resp = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [d.embedding for d in resp.data]
