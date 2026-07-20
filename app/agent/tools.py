"""DB-side tools: athlete state, training log, load analytics, program storage."""

import json
from datetime import date
from typing import Any

from app.db import get_pool
from app.schemas import MemoryDelta, WorkoutLog, WorkoutPlan

DEFAULT_EMAIL = "owner@coach-k.local"  # single-athlete deployment


async def get_or_create_user(email: str = DEFAULT_EMAIL) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        uid = await conn.fetchval(
            """INSERT INTO users (email) VALUES ($1)
               ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
               RETURNING id""",
            email,
        )
    return str(uid)


# ===== Profile (append-only versions) =====

def _merge(base: dict, patch: dict) -> dict:
    """One-level-deep merge so nested objects (e.g. lifts_1rm) accrete, not clobber.
    None values in a patch are ignored — extraction models emit them for
    'unchanged', and null must never erase a known fact."""
    out = dict(base)
    for k, v in patch.items():
        if v is None:
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = {**out[k], **{ik: iv for ik, iv in v.items() if iv is not None}}
        else:
            out[k] = v
    return out


async def get_latest_profile(user_id: str) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchval(
            """SELECT profile FROM user_profiles
               WHERE user_id = $1 ORDER BY version DESC LIMIT 1""",
            user_id,
        )
    return json.loads(row) if row else {}


async def apply_profile_patch(user_id: str, patch: dict, updated_by: str = "agent") -> dict:
    current = await get_latest_profile(user_id)
    merged = _merge(current, patch)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO user_profiles (user_id, version, profile, updated_by)
               VALUES ($1,
                       COALESCE((SELECT MAX(version) FROM user_profiles WHERE user_id = $1), 0) + 1,
                       $2, $3)""",
            user_id, json.dumps(merged), updated_by,
        )
    return merged


# ===== Readiness =====

async def get_recent_readiness(user_id: str, days: int = 14) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT for_date, readiness FROM athlete_readiness
               WHERE user_id = $1 AND for_date > CURRENT_DATE - $2::int
               ORDER BY for_date DESC""",
            user_id, days,
        )
    return [{"date": str(r["for_date"]), **json.loads(r["readiness"])} for r in rows]


async def upsert_readiness(user_id: str, entry: dict, for_date: date | None = None) -> None:
    entry = {k: v for k, v in entry.items() if v is not None}
    if not entry:
        return
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO athlete_readiness (user_id, for_date, readiness)
               VALUES ($1, $2, $3)
               ON CONFLICT (user_id, for_date)
               DO UPDATE SET readiness = athlete_readiness.readiness || EXCLUDED.readiness""",
            user_id, for_date or date.today(), json.dumps(entry),
        )


def _readiness_status(score: int) -> str:
    if score >= 80:
        return "primed"
    if score >= 65:
        return "ready"
    if score >= 50:
        return "moderate"
    return "compromised"


async def store_health_readiness(user_id: str, metrics: dict) -> dict:
    """Store objective HealthKit metrics (sleep_h, hrv_ms, resting_hr) for today
    and derive a 0-100 readiness score against the athlete's OWN trailing
    baseline. Like ACWR, the score stays neutral until there's enough history
    (>=3 prior days of a signal) — a single reading has nothing to compare to."""
    metrics = {k: v for k, v in metrics.items() if v is not None}
    today = str(date.today())
    prior = [r for r in await get_recent_readiness(user_id, days=30) if r.get("date") != today]

    def baseline(key: str) -> float | None:
        vals = [r[key] for r in prior if isinstance(r.get(key), (int, float))]
        return sum(vals) / len(vals) if len(vals) >= 3 else None

    score, weight, parts = 0.0, 0.0, {}
    if (hrv := metrics.get("hrv_ms")):
        hb = baseline("hrv_ms")
        # HRV above baseline = recovered; 0.7x→0, 1.1x→1. Neutral w/o baseline.
        comp = max(0.0, min(1.0, (hrv / hb - 0.7) / 0.4)) if hb else 0.6
        score += 0.6 * comp; weight += 0.6; parts["hrv"] = round(comp, 2)
    if (sleep := metrics.get("sleep_h")) is not None:
        comp = max(0.0, min(1.0, (sleep - 4) / 4))  # 4h→0, 8h→1
        score += 0.3 * comp; weight += 0.3; parts["sleep"] = round(comp, 2)
    if (rhr := metrics.get("resting_hr")):
        rb = baseline("resting_hr")
        # Lower RHR is better; +15% over baseline → 0. Neutral w/o baseline.
        comp = max(0.0, min(1.0, 1 - (rhr - rb) / (0.15 * rb))) if rb else 0.6
        score += 0.1 * comp; weight += 0.1; parts["rhr"] = round(comp, 2)

    stored = {**metrics, "source": "healthkit"}
    baselined = bool(baseline("hrv_ms"))
    if weight:
        stored["readiness_score"] = round(100 * score / weight)
        stored["readiness_status"] = _readiness_status(stored["readiness_score"])
    await upsert_readiness(user_id, stored)
    return {**stored, "baselined": baselined, "components": parts}


# ===== Training log + PR detection (Epley e1RM) =====

def _e1rm(weight: float, reps: int) -> float:
    return weight * (1 + reps / 30)


async def save_workout(user_id: str, log: WorkoutLog) -> dict:
    pool = await get_pool()
    prs: list[str] = []
    async with pool.acquire() as conn, conn.transaction():
        wid = await conn.fetchval(
            """INSERT INTO workouts (user_id, session_rpe, notes)
               VALUES ($1, $2, $3) RETURNING id""",
            user_id, log.session_rpe, log.notes,
        )
        for i, s in enumerate(log.sets):
            is_pr = False
            if s.weight_lbs:
                prior = await conn.fetchval(
                    """SELECT MAX(ws.weight_lbs * (1 + COALESCE(ws.reps, 1) / 30.0))
                       FROM workout_sets ws
                       JOIN workouts w ON w.id = ws.workout_id
                       WHERE w.user_id = $1 AND ws.exercise = $2
                             AND ws.weight_lbs IS NOT NULL""",
                    user_id, s.exercise,
                )
                e1 = _e1rm(s.weight_lbs, s.reps or 1)
                is_pr = prior is None or e1 > float(prior)
            await conn.execute(
                """INSERT INTO workout_sets
                   (workout_id, exercise, set_index, weight_lbs, reps, rir, is_pr)
                   VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                wid, s.exercise, i, s.weight_lbs, s.reps, s.rir, is_pr,
            )
            if is_pr:
                prs.append(s.exercise)
    return {"workout_id": str(wid), "n_sets": len(log.sets), "prs": sorted(set(prs))}


async def log_pain(user_id: str, region: str, severity: int, context: str | None) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO pain_logs (user_id, region, severity, context) VALUES ($1,$2,$3,$4)",
            user_id, region, severity, context,
        )


async def get_load_summary(user_id: str) -> dict:
    """Session load = sRPE proxy (session_rpe × set count). ACWR = 7d avg / 28d avg."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT w.performed_at::date AS day,
                      COALESCE(w.session_rpe, 7) * COUNT(ws.id) AS load
               FROM workouts w
               LEFT JOIN workout_sets ws ON ws.workout_id = w.id
               WHERE w.user_id = $1
                     AND w.performed_at > now() - INTERVAL '28 days'
               GROUP BY w.id, day""",
            user_id,
        )
    today = date.today()
    acute = sum(float(r["load"]) for r in rows if (today - r["day"]).days < 7) / 7
    chronic = sum(float(r["load"]) for r in rows) / 28

    # ACWR is only meaningful once a real chronic baseline exists. With 1-2
    # sessions the ratio is a pure artifact (a lone session always yields
    # 28/7 = 4.0), which reads as a false overtraining alarm. Gate it behind
    # ~2 weeks of history and enough sessions to average against.
    span_days = (today - min((r["day"] for r in rows), default=today)).days
    baselined = span_days >= 14 and len(rows) >= 4
    out = {
        "sessions_28d": len(rows),
        "acute_daily_load": round(acute, 1),
        "chronic_daily_load": round(chronic, 1),
        "acwr": round(acute / chronic, 2) if (baselined and chronic) else None,
    }
    if not baselined:
        out["load_note"] = "building baseline — ACWR needs ~2 weeks of logged training"
    return out


# ===== Programs =====

async def save_program(user_id: str, plan: WorkoutPlan) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        pid = await conn.fetchval(
            """INSERT INTO programs (user_id, name, goal, plan, citations)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            user_id, plan.program_name, plan.goal,
            plan.model_dump_json(),
            json.dumps([c.model_dump() for c in plan.citations]),
        )
    return str(pid)


async def get_program(program_id: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT plan, created_at FROM programs WHERE id = $1", program_id
        )
    if not row:
        return None
    return {"plan": json.loads(row["plan"]), "created_at": str(row["created_at"])}


async def list_programs(user_id: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id::text, name, goal, created_at FROM programs
               WHERE user_id = $1 ORDER BY created_at DESC""",
            user_id,
        )
    return [dict(r) | {"created_at": str(r["created_at"])} for r in rows]


# ===== Chats (thread index; conversation state lives in checkpoints) =====

async def create_chat(user_id: str, title: str = "New chat") -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        cid = await conn.fetchval(
            "INSERT INTO chats (user_id, title) VALUES ($1, $2) RETURNING id",
            user_id, title,
        )
    return str(cid)


async def list_chats(user_id: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id::text, title, created_at FROM chats
               WHERE user_id = $1 ORDER BY created_at DESC""",
            user_id,
        )
    return [dict(r) | {"created_at": str(r["created_at"])} for r in rows]


async def maybe_title_chat(chat_id: str, first_message: str) -> None:
    """First real message names the chat (only while it still has the default)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE chats SET title = $2 WHERE id = $1 AND title = 'New chat'",
            chat_id, first_message.strip()[:60] or "New chat",
        )


# ===== Physique assessments =====

async def save_physique_assessment(
    user_id: str, file_paths: list[str], assessment: dict
) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        for p in file_paths or [""]:
            await conn.execute(
                """INSERT INTO physique_photos (user_id, file_path, assessment)
                   VALUES ($1, $2, $3)""",
                user_id, p, json.dumps(assessment),
            )


async def get_physique_history(user_id: str, limit: int = 3) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT DISTINCT ON (taken_at::date) taken_at, assessment
               FROM physique_photos WHERE user_id = $1 AND assessment IS NOT NULL
               ORDER BY taken_at::date DESC, taken_at DESC LIMIT $2""",
            user_id, limit,
        )
    return [
        {"date": str(r["taken_at"])[:10], **json.loads(r["assessment"])} for r in rows
    ]


# ===== Memory delta application =====

async def apply_memory_delta(user_id: str, delta: MemoryDelta) -> dict[str, Any]:
    """Apply an extracted delta; returns a summary the coach can acknowledge."""
    summary: dict[str, Any] = {}
    if delta.profile_patch:
        await apply_profile_patch(user_id, delta.profile_patch)
        summary["profile_updated"] = list(delta.profile_patch)
    if delta.readiness:
        await upsert_readiness(user_id, delta.readiness.model_dump())
        summary["readiness_logged"] = True
    if delta.workout and delta.workout.sets:
        summary["workout"] = await save_workout(user_id, delta.workout)
    for p in delta.pain:
        await log_pain(user_id, p.region, p.severity, p.context)
    if delta.pain:
        summary["pain_logged"] = [p.region for p in delta.pain]
    return summary


# ===== Today's Workout (living plan, one-tap logging) =====

# Canonical lift -> profile.lifts_1rm key, for suggesting weights from %1RM.
_LIFT_KEY_BY_PATTERN = [
    ("squat", "squat"), ("bench", "bench"), ("deadlift", "deadlift"),
    ("overhead press", "press"), ("press", "press"),
]


def _lift_key_for(exercise: str) -> str | None:
    name = exercise.lower()
    for pattern, key in _LIFT_KEY_BY_PATTERN:
        if pattern in name:
            return key
    return None


def _suggest_weight(exercise: str, intensity: str, one_rms: dict, last_weight: float | None) -> float | None:
    """Best-effort target load: %1RM off the profile, else last time's weight."""
    import re

    key = _lift_key_for(exercise)
    if key and key in one_rms:
        m = re.search(r"(\d+(?:\.\d+)?)\s*%", intensity or "")
        if m:
            return round(one_rms[key] * float(m.group(1)) / 100 / 5) * 5  # round to nearest 5 lbs
    return last_weight


async def get_last_weight(user_id: str, exercise: str) -> float | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(
            """SELECT ws.weight_lbs FROM workout_sets ws
               JOIN workouts w ON w.id = ws.workout_id
               WHERE w.user_id = $1 AND ws.exercise = $2 AND ws.weight_lbs IS NOT NULL
               ORDER BY w.performed_at DESC, ws.set_index DESC LIMIT 1""",
            user_id, exercise,
        )


async def get_active_program(user_id: str) -> dict | None:
    """Most recent program that's actually executable (non-empty weekly_split) —
    skips placeholder/acknowledgment rows the agent sometimes saves mid-conversation."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id::text, plan FROM programs
               WHERE user_id = $1 AND jsonb_array_length(plan -> 'weekly_split') > 0
               ORDER BY created_at DESC LIMIT 1""",
            user_id,
        )
    if not row:
        return None
    return {"id": row["id"], "plan": json.loads(row["plan"])}


async def get_or_init_progress(user_id: str, program_id: str) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO program_progress (user_id, program_id) VALUES ($1, $2)
               ON CONFLICT (user_id, program_id) DO UPDATE SET user_id = EXCLUDED.user_id
               RETURNING day_index, cycle_count""",
            user_id, program_id,
        )
    return {"day_index": row["day_index"], "cycle_count": row["cycle_count"]}


async def get_open_workout(user_id: str, program_id: str, day_index: int) -> dict | None:
    """Today's in-progress session for this program day, if one was started."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id::text FROM workouts
               WHERE user_id = $1 AND program_id = $2 AND program_day_index = $3
                     AND completed_at IS NULL AND performed_at::date = CURRENT_DATE
               ORDER BY performed_at DESC LIMIT 1""",
            user_id, program_id, day_index,
        )
        if not row:
            return None
        sets = await conn.fetch(
            """SELECT exercise, set_index, weight_lbs, reps, rir, is_pr, slot_index
               FROM workout_sets WHERE workout_id = $1 ORDER BY set_index""",
            row["id"],
        )
    return {"workout_id": row["id"], "sets": [dict(s) for s in sets]}


async def get_today(user_id: str) -> dict | None:
    """Everything the Today view needs: the day's plan, suggested weights,
    and any sets already logged this session."""
    prog = await get_active_program(user_id)
    if not prog:
        return None
    days = prog["plan"].get("weekly_split", [])
    if not days:
        return None
    progress = await get_or_init_progress(user_id, prog["id"])
    day = days[progress["day_index"] % len(days)]
    one_rms = (await get_latest_profile(user_id)).get("lifts_1rm", {})

    open_workout = await get_open_workout(user_id, prog["id"], progress["day_index"])
    # Keyed by slot (position in day.exercises), NOT exercise name — a day can
    # list the same lift twice (warmup + working sets) and those must track
    # independently, or logging one silently completes both.
    logged_by_slot: dict[int, list[dict]] = {}
    for s in (open_workout or {}).get("sets", []):
        if s["slot_index"] is not None:
            logged_by_slot.setdefault(s["slot_index"], []).append(s)

    from app.exercises.resolver import media_for

    exercises = []
    for i, ex in enumerate(day.get("exercises", [])):
        last = await get_last_weight(user_id, ex["exercise"])
        media = media_for(ex["exercise"])
        exercises.append({
            **ex,
            "suggested_weight_lbs": _suggest_weight(ex["exercise"], ex.get("intensity", ""), one_rms, last),
            "logged_sets": logged_by_slot.get(i, []),
            "image_urls": media["image_urls"] if media else [],
        })

    return {
        "program_id": prog["id"],
        "program_name": prog["plan"].get("program_name"),
        "day_index": progress["day_index"],
        "cycle_count": progress["cycle_count"],
        "day_label": day.get("day_label"),
        "focus": day.get("focus"),
        "exercises": exercises,
        "workout_id": (open_workout or {}).get("workout_id"),
    }


async def log_today_set(
    user_id: str, program_id: str, day_index: int, slot_index: int, exercise: str,
    weight_lbs: float | None, reps: int | None, rir: float | None,
) -> dict:
    """One-tap incremental logging — creates today's draft workout on the
    first set, appends subsequent sets, flags PRs immediately (for push).
    `slot_index` is the exercise's position in that day's list — required so
    a repeated lift (warmup Back Squat + working Back Squat) tracks as two
    independent rows instead of one logged set completing both."""
    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        wid = await conn.fetchval(
            """SELECT id FROM workouts WHERE user_id = $1 AND program_id = $2
                     AND program_day_index = $3 AND completed_at IS NULL
                     AND performed_at::date = CURRENT_DATE""",
            user_id, program_id, day_index,
        )
        if not wid:
            wid = await conn.fetchval(
                """INSERT INTO workouts (user_id, program_id, program_day_index)
                   VALUES ($1, $2, $3) RETURNING id""",
                user_id, program_id, day_index,
            )
        set_index = await conn.fetchval(
            "SELECT COUNT(*) FROM workout_sets WHERE workout_id = $1 AND slot_index = $2",
            wid, slot_index,
        )
        is_pr = False
        if weight_lbs:
            # PR check is keyed by exercise NAME (not slot) — a PR is about the
            # lift, regardless of which row of the day's plan logged it.
            prior = await conn.fetchval(
                """SELECT MAX(ws.weight_lbs * (1 + COALESCE(ws.reps, 1) / 30.0))
                   FROM workout_sets ws JOIN workouts w ON w.id = ws.workout_id
                   WHERE w.user_id = $1 AND ws.exercise = $2 AND ws.weight_lbs IS NOT NULL""",
                user_id, exercise,
            )
            e1 = _e1rm(weight_lbs, reps or 1)
            is_pr = prior is None or e1 > float(prior)
        await conn.execute(
            """INSERT INTO workout_sets (workout_id, exercise, set_index, weight_lbs, reps, rir, is_pr, slot_index)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            wid, exercise, set_index, weight_lbs, reps, rir, is_pr, slot_index,
        )
    return {"workout_id": str(wid), "set_index": set_index, "is_pr": is_pr}


async def resolve_open_slot(
    user_id: str, program_id: str, day_index: int, exercise: str, weight_lbs: float | None = None,
) -> int:
    """For voice logging: Haiku matches an exercise NAME, but a day can list
    it twice (warmup vs. working sets at very different loads). Disambiguate
    by the spoken weight first — "320 for 6" clearly means the working slot,
    not a 240 lb warmup — falling back to day order (warmup-before-working)
    when no weight was given or it doesn't clearly favor one slot."""
    prog = await get_active_program(user_id)
    days = (prog or {}).get("plan", {}).get("weekly_split", [])
    if not prog or not (0 <= day_index < len(days)):
        return 0
    day_exercises = days[day_index].get("exercises", [])
    matches = [i for i, ex in enumerate(day_exercises) if ex["exercise"] == exercise]
    if not matches:
        return 0

    open_workout = await get_open_workout(user_id, program_id, day_index)
    counts: dict[int, int] = {}
    for s in (open_workout or {}).get("sets", []):
        if s["slot_index"] is not None:
            counts[s["slot_index"]] = counts.get(s["slot_index"], 0) + 1

    open_matches = [i for i in matches if counts.get(i, 0) < day_exercises[i].get("sets", 0)]
    if not open_matches:
        return matches[-1]
    if len(open_matches) == 1 or weight_lbs is None:
        return open_matches[0]

    one_rms = (await get_latest_profile(user_id)).get("lifts_1rm", {})
    by_distance = []
    for i in open_matches:
        ex = day_exercises[i]
        last = await get_last_weight(user_id, exercise)
        suggested = _suggest_weight(exercise, ex.get("intensity", ""), one_rms, last)
        if suggested is not None:
            by_distance.append((abs(suggested - weight_lbs), i))
    if by_distance:
        return min(by_distance)[1]
    return open_matches[0]


async def finish_today(user_id: str, program_id: str, day_index: int, session_rpe: float | None) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            """UPDATE workouts SET completed_at = now(), session_rpe = COALESCE($4, session_rpe)
               WHERE user_id = $1 AND program_id = $2 AND program_day_index = $3
                     AND completed_at IS NULL AND performed_at::date = CURRENT_DATE""",
            user_id, program_id, day_index, session_rpe,
        )
        prog = await conn.fetchval(
            "SELECT plan FROM programs WHERE id = $1", program_id
        )
        n_days = len(json.loads(prog).get("weekly_split", [])) or 1
        next_index = (day_index + 1) % n_days
        next_cycle_incr = 1 if next_index == 0 else 0
        await conn.execute(
            """UPDATE program_progress SET day_index = $3, cycle_count = cycle_count + $4,
                      updated_at = now()
               WHERE user_id = $1 AND program_id = $2""",
            user_id, program_id, next_index, next_cycle_incr,
        )


# ===== Push subscriptions =====

async def save_push_subscription(user_id: str, subscription: dict) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """INSERT INTO push_subscriptions (user_id, endpoint, subscription)
               VALUES ($1, $2, $3)
               ON CONFLICT (endpoint) DO UPDATE SET subscription = EXCLUDED.subscription""",
            user_id, subscription["endpoint"], json.dumps(subscription),
        )


async def list_push_subscriptions(user_id: str) -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT subscription FROM push_subscriptions WHERE user_id = $1", user_id
        )
    return [json.loads(r["subscription"]) for r in rows]


async def remove_push_subscription(endpoint: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM push_subscriptions WHERE endpoint = $1", endpoint)


# ===== Context assembly =====

def format_context(
    profile: dict, readiness: list[dict], load: dict, sources: str | None
) -> str:
    parts = [
        "ATHLETE PROFILE:\n" + (json.dumps(profile, indent=1) if profile else "(empty — still learning this athlete)"),
        f"READINESS (last 14d, newest first):\n{json.dumps(readiness, indent=1) if readiness else '(no entries)'}",
        f"TRAINING LOAD:\n{json.dumps(load)}",
    ]
    if sources:
        parts.append("SOURCES (cite by book + page; reference chunk_id in citations):\n" + sources)
    return "\n\n".join(parts)
