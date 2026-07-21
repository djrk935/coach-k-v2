-- Per-day markers: rest, travel, game (mesocycle calendar).
CREATE TABLE IF NOT EXISTS calendar_markers (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    for_date    DATE NOT NULL,
    kind        TEXT NOT NULL CHECK (kind IN ('rest', 'travel', 'game')),
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, for_date)
);

CREATE INDEX IF NOT EXISTS idx_calendar_markers_user_date
    ON calendar_markers (user_id, for_date);
