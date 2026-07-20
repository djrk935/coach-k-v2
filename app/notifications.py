"""Web push — proactive coaching (PR shouts, readiness nudges, streak breaks)."""

import json
import logging

from pywebpush import WebPushException, webpush

from app.agent import tools
from app.config import settings

log = logging.getLogger("coachk.push")


async def notify(user_id: str, title: str, body: str, url: str = "/") -> None:
    if not (settings.vapid_private_key and settings.vapid_public_key):
        return
    subs = await tools.list_push_subscriptions(user_id)
    payload = json.dumps({"title": title, "body": body, "url": url})
    for sub in subs:
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_subject},
            )
        except WebPushException as e:
            log.warning("push failed (%s): %s", sub.get("endpoint", "?")[:60], e)
            if e.response is not None and e.response.status_code in (404, 410):
                await tools.remove_push_subscription(sub["endpoint"])
