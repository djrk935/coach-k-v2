"""Proactive coaching — the agent initiates instead of waiting to be opened.

Daily job: readiness check-in nudge, soft-day from HealthKit/ACWR, inactivity
ping. Weekly job: Sunday review card with wins + next-week focus.
"""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agent import tools
from app.coaching.adapt import adaptation_for
from app.coaching.debrief import weekly_review_payload
from app.notifications import notify

log = logging.getLogger("coachk.scheduler")


async def _check_in_on(user_id: str) -> None:
    today_plan = await tools.get_today(user_id)
    readiness = await tools.get_recent_readiness(user_id, days=1)
    load = await tools.get_load_summary(user_id)
    adapt = adaptation_for(readiness[0] if readiness else None, load, None)

    # HealthKit / readiness soft-day proactive note
    if adapt.get("soft_day") and today_plan:
        await notify(
            user_id, "Coach K — soft day",
            "Readiness/load says ease up today. Open Today — volume is already trimmed.",
            url="/",
        )
        return

    if today_plan and not readiness:
        await notify(
            user_id, "Coach K",
            f"Today: {today_plan['day_label']}. How'd you sleep? Check in before you lift.",
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
            "Haven't seen you in a few days — everything OK? Resume, repeat, or take a light makeup.",
        )


async def daily_checkins() -> None:
    user_id = await tools.get_or_create_user()
    try:
        await _check_in_on(user_id)
    except Exception:
        log.exception("daily check-in failed for %s", user_id)


async def weekly_reviews() -> None:
    user_id = await tools.get_or_create_user()
    try:
        profile = await tools.get_latest_profile(user_id)
        readiness = await tools.get_recent_readiness(user_id, days=14)
        load = await tools.get_load_summary(user_id)
        prs = await tools.recent_prs(user_id, days=14)
        review = weekly_review_payload(profile, readiness, load, [], prs)
        body = (review["focuses"][0] if review["focuses"] else "Open Coach K for your weekly review.")
        await notify(user_id, review["title"], body[:180], url="/")
    except Exception:
        log.exception("weekly review failed for %s", user_id)


def start_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_checkins, CronTrigger(hour=8, minute=0), id="daily_checkins")
    scheduler.add_job(weekly_reviews, CronTrigger(day_of_week="sun", hour=18, minute=0), id="weekly_reviews")
    scheduler.start()
    return scheduler
