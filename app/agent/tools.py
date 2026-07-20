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
