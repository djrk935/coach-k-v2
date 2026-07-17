-- Chat threads (conversation state lives in LangGraph checkpoints; this table
-- is the user-facing index) + physique photo assessments for progress tracking.
-- Existing deployments: psql coachk -f migrations/002_chats_physique.sql

CREATE TABLE chats (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT NOT NULL DEFAULT 'New chat',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_chats_user ON chats (user_id, created_at DESC);

CREATE TABLE physique_photos (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    taken_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    file_path   TEXT NOT NULL,
    assessment  JSONB
);
CREATE INDEX idx_physique_user ON physique_photos (user_id, taken_at DESC);
