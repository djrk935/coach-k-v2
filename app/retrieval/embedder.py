"""Local embeddings — BAAI/bge-base-en-v1.5 via fastembed (ONNX).

Free, private, no API dependency. Query embedding gets BGE's retrieval
prefix via query_embed; passages are embedded as-is.
"""

import asyncio

from fastembed import TextEmbedding

from app.config import settings

_model: TextEmbedding | None = None


def _get() -> TextEmbedding:
    global _model
    if _model is None:  # first call downloads the ONNX model (~130 MB), then cached
        _model = TextEmbedding(settings.embed_model)
    return _model


async def embed_passages(texts: list[str]) -> list[list[float]]:
    def run() -> list[list[float]]:
        return [e.tolist() for e in _get().embed(texts, batch_size=64)]

    return await asyncio.to_thread(run)


async def embed_query(query: str) -> list[float]:
    def run() -> list[float]:
        return next(iter(_get().query_embed(query))).tolist()

    return await asyncio.to_thread(run)
