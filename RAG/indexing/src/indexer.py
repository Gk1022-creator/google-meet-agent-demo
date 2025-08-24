# src/indexer.py
from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import uuid
import logging

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from qdrant_client.http.models import PointStruct

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _get_expected_dim(client: QdrantClient, collection: str, fallback: Optional[int] = None) -> Optional[int]:
    """Try to read vector size from collection metadata. Return fallback if unavailable."""
    try:
        info = client.get_collection(collection_name=collection)
        # info may be object with attribute 'vectors_config' or a dict
        vc = None
        if hasattr(info, "vectors_config") and info.vectors_config is not None:
            vc = info.vectors_config
            size = getattr(vc, "size", None)
            if size:
                return int(size)
        # fallback parsing for dict-like return
        if isinstance(info, dict):
            # some qdrant client versions return {"vectors": {"size": N, ...}}
            for key in ("vectors", "vectors_config"):
                if key in info and isinstance(info[key], dict):
                    size = info[key].get("size")
                    if size:
                        return int(size)
    except Exception:
        # can't get collection info — leave fallback
        pass
    return fallback


def _normalize_vector(v: Any, expected_dim: Optional[int] = None) -> Optional[List[float]]:
    """Normalize various embedding shapes to a flat list[float].
    Returns None if cannot normalize.
    Handles:
      - {'embedding':[...]}
      - [[...]] -> unwrap
      - nested lists -> try to find inner list of correct length
    """
    if v is None:
        return None

    # unwrap dict forms
    if isinstance(v, dict):
        if "embedding" in v:
            v = v["embedding"]
        elif "vector" in v:
            v = v["vector"]

    # unwrap if single-item list containing a list: [[...]] -> [...]
    if isinstance(v, list) and len(v) == 1 and isinstance(v[0], list):
        v = v[0]

    # if list of lists, try to pick the first inner list that looks like a vector
    if isinstance(v, list) and any(isinstance(el, list) for el in v):
        # Try to find inner list with expected_dim
        if expected_dim:
            for el in v:
                if isinstance(el, list) and len(el) == expected_dim and all(isinstance(x, (int, float)) for x in el):
                    v = el
                    break
        # otherwise try first inner list of numbers
        if isinstance(v, list) and any(isinstance(el, list) for el in v):
            for el in v:
                if isinstance(el, list) and all(isinstance(x, (int, float)) for x in el):
                    v = el
                    break
        # if still nested, flatten one level as a last resort
        if isinstance(v, list) and any(isinstance(el, list) for el in v):
            flat = []
            for el in v:
                if isinstance(el, list):
                    flat.extend(el)
                else:
                    flat.append(el)
            v = flat

    # final check: must be list of numbers
    if isinstance(v, list) and all(isinstance(x, (int, float)) for x in v):
        v = [float(x) for x in v]
        # final length check if expected_dim provided
        if expected_dim and len(v) != expected_dim:
            return None
        return v

    return None


def ensure_collection(client: QdrantClient, name: str, vector_size: int, distance: str = "COSINE"):
    # Create or ensure collection (case-insensitive distance)
    dist = getattr(qm.Distance, distance.upper())
    try:
        client.get_collection(collection_name=name)
        logger.info("Collection '%s' exists.", name)
    except Exception:
        client.recreate_collection(
            collection_name=name,
            vectors_config=qm.VectorParams(size=vector_size, distance=dist),
        )
        logger.info("Collection '%s' created (size=%s).", name, vector_size)


def upsert_points(
    client: QdrantClient,
    collection: str,
    vectors: List[Any],           # raw embeddings (may be nested / dicts)
    payloads: List[Dict[str, Any]],
    ids: Optional[List[Any]] = None,
    expected_dim: Optional[int] = None,
    batch_wait: bool = True
) -> Tuple[int, int]:
    """
    Upsert points with robust normalization.
    Returns (num_upserted, num_skipped).
    - vectors: list of raw embedding objects (list/[[...]]/dict)
    - payloads: list of payload dicts (same length)
    - ids: optional original ids (strings) - these will be stored in payload as '_orig_id'
    - expected_dim: if provided, validate vector length (or will try to query collection)
    """
    if ids is None:
        ids = [None] * len(vectors)

    # try to infer expected_dim from collection if not provided
    if expected_dim is None:
        expected_dim = _get_expected_dim(client, collection, fallback=None)

    points = []
    upserted = 0
    skipped = 0

    for raw_vec, payload, orig_id in zip(vectors, payloads, ids):
        vec = _normalize_vector(raw_vec, expected_dim=expected_dim)
        if not vec:
            skipped += 1
            logger.debug("Skipping vector (could not normalize or empty). orig_id=%s", orig_id)
            continue

        # final dimension check (if known)
        if expected_dim and len(vec) != expected_dim:
            skipped += 1
            logger.debug("Skipping vector with wrong dimension (expected %s got %s). orig_id=%s", expected_dim, len(vec), orig_id)
            continue

        # prepare payload copy and include original id for traceability
        pl = dict(payload) if isinstance(payload, dict) else {"text": str(payload)}
        if orig_id is not None:
            pl["_orig_id"] = orig_id

        # use a safe UUID for qdrant point id
        pid = str(uuid.uuid4())

        points.append(PointStruct(id=pid, vector=vec, payload=pl))
        upserted += 1

    if points:
        # upsert in one call (small number). If large, caller should call in batches.
        client.upsert(collection_name=collection, points=points, wait=batch_wait)
        logger.info("Upserted %d points (skipped %d).", upserted, skipped)
    else:
        logger.warning("No valid points to upsert (skipped %d).", skipped)

    return upserted, skipped
