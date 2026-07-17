"""Batch-ingest the book library. One failure doesn't stop the rest."""

import asyncio
import time
from pathlib import Path

from app.db import close_pool, get_pool
from app.ingestion.pipeline import ingest_pdf

LIB = Path(__file__).parent / "library"

BOOKS = [
    ("strength-zatsiorsky.pdf", "Science and Practice of Strength Training (2nd ed.)", "Zatsiorsky & Kraemer"),
    ("periodization-bompa.pdf", "Periodization: Theory and Methodology of Training (5th ed.)", "Bompa & Haff"),
    ("hypertrophy-schoenfeld.pdf", "Science and Development of Muscle Hypertrophy (2nd ed.)", "Brad Schoenfeld"),
    ("pyramid-helms.pdf", "The Muscle and Strength Training Pyramid: Training (v2.0)", "Eric Helms"),
    ("oly-weightlifting.pdf", "Olympic Weightlifting: A Complete Guide", "Greg Everett"),
    ("jump-attack.pdf", "Jump Attack", "Tim Grover"),
    ("tactical-barbell.epub", "Tactical Barbell", "K. Black"),
]


async def main() -> None:
    for fname, title, author in BOOKS:
        path = LIB / fname
        t0 = time.time()
        print(f"→ {title} ...", flush=True)
        try:
            doc_id = await ingest_pdf(path, title, author)
            pool = await get_pool()
            async with pool.acquire() as conn:
                n = await conn.fetchval(
                    "SELECT count(*) FROM doc_chunks WHERE document_id = $1", doc_id
                )
                nt = await conn.fetchval(
                    "SELECT count(*) FROM doc_chunks WHERE document_id = $1 AND content_type='table'",
                    doc_id,
                )
            print(f"  ✓ {n} chunks ({nt} tables) in {time.time() - t0:.0f}s — {doc_id}", flush=True)
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {str(e)[:300]}", flush=True)
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
