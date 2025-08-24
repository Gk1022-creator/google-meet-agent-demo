
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from .config import settings

_qclient = None
def _get_qclient():
    global _qclient
    if _qclient is None:
        _qclient = QdrantClient(url=settings.qdrant_url)
    return _qclient

def search_qdrant(vector: List[float], top_k: int = 8) -> List[Dict[str, Any]]:
    client = _get_qclient()
    vector = vector[0]
    res = client.search(collection_name=settings.qdrant_collection, query_vector=vector, limit=top_k, with_payload=True)
    hits = []
    for h in res:
        hits.append({"id": str(h.id), "score": float(h.score), "payload": h.payload or {}})
    return hits

# Simple tool registry
TOOLS = {
    "qdrant.search": search_qdrant
}
