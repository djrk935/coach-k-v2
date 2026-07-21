-- Native iOS APNs device tokens (alongside web push_subscriptions).
CREATE TABLE IF NOT EXISTS apns_devices (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_token TEXT NOT NULL,
    sandbox     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, device_token)
);
CREATE INDEX IF NOT EXISTS idx_apns_devices_user ON apns_devices (user_id);
