-- Living "Today's Workout" execution state + push notification subscriptions.
-- Existing deployments: psql coachk -f migrations/004_today_push.sql

-- Which day of the active program's rotation is next, and how many times
-- the rotation has completed (drives simple weekly progression cues).
CREATE TABLE program_progress (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    program_id   UUID NOT NULL REFERENCES programs(id) ON DELETE CASCADE,
    day_index    INT NOT NULL DEFAULT 0,
    cycle_count  INT NOT NULL DEFAULT 0,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, program_id)
);

-- A workout started from Today but not yet finished (draft state for
-- one-tap incremental set logging, vs. the all-at-once /log chat flow).
ALTER TABLE workouts ADD COLUMN completed_at TIMESTAMPTZ;
ALTER TABLE workouts ADD COLUMN program_day_index INT;

CREATE TABLE push_subscriptions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint     TEXT NOT NULL UNIQUE,
    subscription JSONB NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
