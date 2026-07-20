# Coach K v2

Science-grounded AI strength coach. RAG over a private library of fitness
textbooks (table-aware), evolving athlete state, periodized programs with real
citations, branded PDF artifacts.

## Stack

FastAPI · PostgreSQL + pgvector · LangGraph (agent loop, Postgres-checkpointed) ·
LlamaParse (ingestion) · fastembed / BGE (local embeddings) · WeasyPrint (PDF) ·
React 19 + Tailwind 4

## Setup

```bash
# Backend
uv sync
createdb coachk    # migrations run automatically on first ./run.sh
cp .env.example .env            # fill ANTHROPIC_API_KEY + APP_PASSWORD for prod-like dev
# macOS: WeasyPrint needs pango — brew install pango

# Exercise form illustrations (free-exercise-db, ~100MB, one-time)
./scripts/fetch_exercise_media.sh

# Ingest your library (embeddings run locally — no OpenAI key needed)
uv run python -m app.ingestion.pipeline ~/library/supertraining.pdf "Supertraining" --author "Siff"

# Run
./run.sh                                     # backend on :8000 (sets DYLD path for WeasyPrint)
cd frontend && npm install && npm run dev    # http://localhost:5173
```

## Deploy + iPhone

See **[DEPLOY.md](DEPLOY.md)** for DigitalOcean (Docker Compose or App Platform with
HTTPS) and installing the native iOS app on your phone.

## How it works

```
user msg → route (haiku) → load athlete state (profile, readiness 14d, ACWR)
        → retrieve (pgvector hybrid, tables boosted for programming)
        → act (opus: program JSON w/ validated citations | grounded coaching)
        → update memory (extract MemoryDelta → versioned profile / readiness / logs)
```

- **Embeddings are local** (`BAAI/bge-base-en-v1.5` via fastembed, 768d) — the
  library never leaves the machine and ingestion costs nothing.
- **Conversation memory is durable** — LangGraph is checkpointed to Postgres, so
  a restart resumes the thread mid-conversation.
- Programs are `WorkoutPlan` JSON → Jinja2 → WeasyPrint → branded PDF at
  `/api/programs/{id}/pdf`. Citations are filtered to actually-retrieved chunks —
  the agent cannot invent sources.
- Profile is append-only versioned JSONB; readiness is one row per day; PRs are
  auto-detected via Epley e1RM against full history.
- **ACWR** is withheld until ~2 weeks of training is logged, so a cold start
  doesn't fire a false overtraining alarm.
