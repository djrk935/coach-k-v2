CREATE EXTENSION IF NOT EXISTS vector;

-- ===== Identity & evolving state =====
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       TEXT UNIQUE NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Append-only versions; latest = current athlete model
CREATE TABLE user_profiles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    version     INT NOT NULL,
    profile     JSONB NOT NULL,   -- goals, 1RMs, training age, equipment, injuries, MEV/MRV
    updated_by  TEXT NOT NULL,    -- 'agent' | 'user'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, version)
);

-- One row per day; agent reads a 14-day window for trends (ACWR, fatigue)
CREATE TABLE athlete_readiness (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    for_date    DATE NOT NULL,
    readiness   JSONB NOT NULL,   -- sleep_h, soreness, stress, motivation, derived_score
    UNIQUE (user_id, for_date)
);

-- ===== Training log =====
CREATE TABLE programs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    goal        TEXT,             -- hypertrophy | strength | peaking
    plan        JSONB NOT NULL,   -- structured WorkoutPlan
    citations   JSONB,            -- [{chunk_id, book, page, principle}]
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workouts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_id   UUID REFERENCES programs(id) ON DELETE SET NULL,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    session_rpe  NUMERIC(3,1),
    notes        TEXT
);

CREATE TABLE workout_sets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id  UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    exercise    TEXT NOT NULL,
    set_index   INT NOT NULL,
    weight_kg   NUMERIC(6,2),
    reps        INT,
    rir         NUMERIC(3,1),
    is_pr       BOOLEAN DEFAULT FALSE
);

CREATE TABLE pain_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    logged_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    region      TEXT NOT NULL,
    severity    INT CHECK (severity BETWEEN 0 AND 10),
    context     TEXT
);

-- ===== Private document RAG =====
CREATE TABLE documents (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title        TEXT NOT NULL,
    author       TEXT,
    source_hash  TEXT UNIQUE,     -- sha256 → idempotent re-ingestion
    page_count   INT,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE doc_chunks (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id  UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index  INT NOT NULL,
    content      TEXT NOT NULL,
    content_type TEXT NOT NULL,   -- 'prose' | 'table' | 'figure_caption'
    page_start   INT,
    metadata     JSONB NOT NULL DEFAULT '{}',  -- section path, book, table_data
    embedding    vector(768) NOT NULL,
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_chunks_embedding ON doc_chunks
    USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_metadata ON doc_chunks USING gin (metadata);
CREATE INDEX idx_readiness_user_date ON athlete_readiness (user_id, for_date DESC);
CREATE INDEX idx_profiles_latest ON user_profiles (user_id, version DESC);
