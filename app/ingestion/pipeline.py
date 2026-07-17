"""PDF → table-aware markdown → chunks → embeddings → pgvector.

Tables (%1RM charts, Prilepin, MEV/MRV landmarks) become their own chunks
with content_type='table' so retrieval can target them as data.
"""

import hashlib
import json
import re
from pathlib import Path

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_parse import LlamaParse

from app.config import settings
from app.db import get_pool

# A markdown pipe-table: header row, separator row, 1+ data rows.
_TABLE_RE = re.compile(r"(?:^\|.+\|\s*$\n?){2,}", re.MULTILINE)

_PARSING_INSTRUCTION = (
    "This is a strength & conditioning / biomechanics textbook. "
    "Preserve every table exactly as a markdown table (rep schemes, %1RM charts, "
    "Prilepin's table, volume landmarks). Keep column headers. "
    "Preserve equations and figure captions."
)


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _split_page(text: str) -> list[tuple[str, str]]:
    """Split page markdown into (content_type, content) chunks.

    Tables are lifted out whole; surrounding prose is sentence-split.
    """
    chunks: list[tuple[str, str]] = []
    splitter = SentenceSplitter(chunk_size=700, chunk_overlap=80)

    last_end = 0
    for m in _TABLE_RE.finditer(text):
        prose = text[last_end : m.start()].strip()
        if prose:
            chunks.extend(("prose", c) for c in splitter.split_text(prose))
        chunks.append(("table", m.group().strip()))
        last_end = m.end()

    tail = text[last_end:].strip()
    if tail:
        chunks.extend(("prose", c) for c in splitter.split_text(tail))
    return chunks


async def ingest_pdf(path: Path, title: str, author: str | None = None) -> str:
    """Ingest one textbook. Idempotent by sha256. Returns document id."""
    source_hash = _hash_file(path)
    pool = await get_pool()

    async with pool.acquire() as conn:
        existing = await conn.fetchval(
            "SELECT id FROM documents WHERE source_hash = $1", source_hash
        )
        if existing:
            return str(existing)

    # 1. Parse: one markdown Document per page, tables preserved.
    parser = LlamaParse(
        api_key=settings.llama_cloud_api_key,
        result_type="markdown",
        parsing_instruction=_PARSING_INSTRUCTION,
    )
    pages: list[Document] = await parser.aload_data(str(path))

    # 2. Chunk, tracking page + section for citation quality.
    records: list[tuple[str, str, int | None, dict]] = []  # (type, content, page, meta)
    section = ""
    for page in pages:
        page_num = page.metadata.get("page_number") or page.metadata.get("page_label")
        for content_type, content in _split_page(page.text):
            if heading := re.search(r"^#{1,3} (.+)$", content, re.MULTILINE):
                section = heading.group(1).strip()
            meta = {"book": title, "section": section}
            if content_type == "table":
                meta["table_data"] = content  # verbatim markdown grid
            records.append((content_type, content, page_num, meta))

    # 3. Embed in batches.
    embed = OpenAIEmbedding(
        model=settings.embed_model,
        dimensions=settings.embed_dim,
        api_key=settings.openai_api_key,
    )
    vectors = await embed.aget_text_embedding_batch([r[1] for r in records])

    # 4. Persist atomically.
    async with pool.acquire() as conn, conn.transaction():
        doc_id = await conn.fetchval(
            """INSERT INTO documents (title, author, source_hash, page_count)
               VALUES ($1, $2, $3, $4) RETURNING id""",
            title, author, source_hash, len(pages),
        )
        await conn.executemany(
            """INSERT INTO doc_chunks
               (document_id, chunk_index, content, content_type, page_start, metadata, embedding)
               VALUES ($1, $2, $3, $4, $5, $6, $7)""",
            [
                (doc_id, i, content, ctype, page, json.dumps(meta), vec)
                for i, ((ctype, content, page, meta), vec) in enumerate(zip(records, vectors))
            ],
        )
    return str(doc_id)


if __name__ == "__main__":
    import argparse
    import asyncio

    ap = argparse.ArgumentParser(description="Ingest a fitness PDF into the library")
    ap.add_argument("path", type=Path)
    ap.add_argument("title")
    ap.add_argument("--author")
    args = ap.parse_args()

    doc_id = asyncio.run(ingest_pdf(args.path, args.title, args.author))
    print(f"ingested: {doc_id}")
