"""Proactive coaching — the agent initiates instead of waiting to be opened.

One daily job: readiness check-in nudge, "due for training today," inactivity
ping, and an ACWR-spike warning. Single-athlete deployment for now (see
tools.DEFAULT_EMAIL) — the job iterates users so this is ready for accounts
without a rewrite.
"""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agent import tools
from app.notifications import notify

log = logging.getLogger("coachk.scheduler")


async def _check_in_on(user_id: str) -> None:
    today_plan = await tools.get_today(user_id)
    readiness = await tools.get_recent_readiness(user_id, days=1)
    load = await tools.get_load_summary(user_id)

    if today_plan and not readiness:
        await notify(
            user_id, "Coach K",
            f"Today: {today_plan['day_label']}. How'd you sleep? Log in and let's go.",
            url="/",
        )
        return

    if load.get("acwr") and load["acwr"] > 1.5:
        await notify(
            user_id, "Coach K — heads up",
            f"Your training load spiked (ACWR {load['acwr']}). Consider backing off today.",
        )
        return

    pool = await tools.get_pool()
    async with pool.acquire() as conn:
        last = await conn.fetchval(
            "SELECT MAX(performed_at) FROM workouts WHERE user_id = $1", user_id
        )
    if last and (datetime.now(timezone.utc) - last) > timedelta(days=5):
        await notify(
            user_id, "Coach K",
            "Haven't seen you in a few days — everything OK? Your program's still here.",
        )


async def daily_checkins() -> None:
    user_id = await tools.get_or_create_user()
    try:
        await _check_in_on(user_id)
    except Exception:
        log.exception("daily check-in failed for %s", user_id)


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_checkins, CronTrigger(hour=8, minute=0), id="daily_checkins")
    scheduler.start()
    return scheduler
