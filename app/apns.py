"""APNs helpers — register device tokens and fan out with web push.

Send path activates only when APNS_KEY_ID / APNS_TEAM_ID / APNS_AUTH_KEY are set.
Without credentials, tokens are stored for later and notify() no-ops for APNs.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from app.config import settings

log = logging.getLogger("coachk.apns")


def apns_configured() -> bool:
    return bool(settings.apns_key_id and settings.apns_team_id and settings.apns_auth_key)


def _load_auth_key() -> str:
    raw = (settings.apns_auth_key or "").strip()
    if not raw:
        return ""
    if raw.startswith("-----BEGIN"):
        return raw
    path = Path(raw)
    if path.is_file():
        return path.read_text()
    return raw


def _apns_jwt() -> str | None:
    if not apns_configured():
        return None
    try:
        import jwt  # PyJWT
    except ImportError:
        log.warning("PyJWT not installed — APNs send disabled")
        return None
    key = _load_auth_key()
    if not key:
        return None
    now = int(time.time())
    return jwt.encode(
        {"iss": settings.apns_team_id, "iat": now},
        key,
        algorithm="ES256",
        headers={"alg": "ES256", "kid": settings.apns_key_id},
    )


async def send_apns(device_token: str, title: str, body: str, *, sandbox: bool) -> bool:
    """Push one alert. Returns False on hard failure (caller may drop the token)."""
    token_jwt = _apns_jwt()
    if not token_jwt:
        return True  # not configured — treat as soft success (don't delete token)

    host = "api.sandbox.push.apple.com" if sandbox else "api.push.apple.com"
    url = f"https://{host}/3/device/{device_token}"
    payload = {
        "aps": {
            "alert": {"title": title, "body": body},
            "sound": "default",
        }
    }
    headers = {
        "authorization": f"bearer {token_jwt}",
        "apns-topic": settings.apns_bundle_id,
        "apns-push-type": "alert",
        "apns-priority": "10",
        "content-type": "application/json",
    }
    try:
        import httpx
    except ImportError:
        log.warning("httpx not installed — APNs send disabled")
        return True

    try:
        async with httpx.AsyncClient(http2=True, timeout=15.0) as client:
            res = await client.post(url, content=json.dumps(payload), headers=headers)
        if res.status_code == 200:
            return True
        log.warning("APNs %s: %s %s", device_token[:12], res.status_code, res.text[:200])
        return res.status_code not in (410, 400)
    except Exception as e:
        log.warning("APNs send failed: %s", e)
        return True
