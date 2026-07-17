"""Hybrid retrieval: pgvector ANN + metadata filters + content-type boost."""

from pgvector import Vector

from app.db import get_pool
from app.retrieval.embedder import embed_query

# Soft boost: prefer_type chunks rank ~0.05 cosine-distance closer, but
# other types still surface if clearly more relevant.
_SEARCH_SQL = """
SELECT c.id::text, c.content, c.content_type, c.metadata, c.page_start,
       d.title AS book, d.author,
       (c.embedding <=> $1) AS distance
FROM doc_chunks c
JOIN documents d ON d.id = c.document_id
WHERE ($4::text IS NULL OR d.title = $4)
ORDER BY (c.embedding <=> $1)
         - CASE WHEN $2::text IS NOT NULL AND c.content_type = $2 THEN 0.05 ELSE 0 END
LIMIT $3
"""


async def hybrid_search(
    query: str,
    k: int = 8,
    prefer_type: str | None = None,  # 'table' for programming, None for Q&A
    book: str | None = None,
) -> list[dict]:
    vec = await embed_query(query)
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(_SEARCH_SQL, Vector(vec), prefer_type, k, book)
    return [dict(r) for r in rows]


def format_hits_for_prompt(hits: list[dict]) -> str:
    """Render hits as a citation-ready context block for the agent."""
    blocks = []
    for h in hits:
        loc = f"{h['book']}" + (f", p.{h['page_start']}" if h["page_start"] else "")
        blocks.append(
            f"[chunk:{h['id']} | {loc} | {h['content_type']}]\n{h['content']}"
        )
    return "\n\n---\n\n".join(blocks)
