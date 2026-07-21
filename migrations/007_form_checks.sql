-- Form-check assessments from Today video keyframes.
CREATE TABLE IF NOT EXISTS form_checks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise    TEXT NOT NULL,
    taken_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    note        TEXT,
    file_paths  JSONB NOT NULL DEFAULT '[]'::jsonb,
    assessment  JSONB
);
CREATE INDEX IF NOT EXISTS idx_form_checks_user
    ON form_checks (user_id, taken_at DESC);
