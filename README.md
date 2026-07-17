# Coach K v2

Science-grounded AI strength coach. RAG over a private library of fitness
textbooks (table-aware), evolving athlete state, periodized programs with real
citations, branded PDF artifacts.

## Stack

FastAPI · PostgreSQL + pgvector · LangGraph (agent loop) · LlamaParse/LlamaIndex
(ingestion) · WeasyPrint (PDF) · React 19 + Tailwind 4

## Setup

```bash
# Backend
uv sync
createdb coachk && psql coachk -f migrations/001_init.sql
cp .env.example .env            # fill keys
# macOS: WeasyPrint needs pango — brew install pango

# Ingest your library
uv run python -m app.ingestion.pipeline ~/library/supertraining.pdf "Supertraining" --author "Siff"

# Run (macOS: export DYLD_FALLBACK_LIBRARY_PATH="$(brew --prefix)/lib" for WeasyPrint)
uv run uvicorn app.main:app --reload --port 8000
cd frontend && npm install && npm run dev   # http://localhost:5173
```

## How it works

```
user msg → route (haiku) → load athlete state (profile, readiness 14d, ACWR)
        → retrieve (pgvector hybrid, tables boosted for programming)
        → act (opus: program JSON w/ validated citations | grounded coaching)
        → update memory (extract MemoryDelta → versioned profile / readiness / logs)
```

- Programs are `WorkoutPlan` JSON → Jinja2 → WeasyPrint → branded PDF at
  `/api/programs/{id}/pdf`. Citations are filtered to actually-retrieved chunks —
  the agent cannot invent sources.
- Profile is append-only versioned JSONB; readiness is one row per day; PRs are
  auto-detected via Epley e1RM against full history.
