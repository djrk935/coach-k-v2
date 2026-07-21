"""FastAPI surface: SSE chat, ingestion, program PDFs, dashboard."""

import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from pydantic import BaseModel

from app.agent import tools
from app.agent.graph import build_graph, parse_voice_set
from app.artifacts.renderer import render_program_pdf
from app.config import settings
from app.db import close_pool
from app.migrate import apply_migrations
from app.ingestion.pipeline import ingest_pdf
from app.notifications import notify
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    applied = await asyncio.to_thread(apply_migrations, settings.database_url)
    if applied:
        print(f"migrations applied: {', '.join(applied)}")

    # Durable per-user chat memory: the Postgres saver survives restarts, so
    # Coach K resumes a conversation mid-thread instead of forgetting it.
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        await saver.setup()  # idempotent: creates checkpoint tables if absent
        app.state.agent = build_graph(saver)
        scheduler = start_scheduler()
        yield
        scheduler.shutdown(wait=False)
    await close_pool()


app = FastAPI(title="Coach K v2", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public paths when APP_PASSWORD gates the API: health probes and exercise
# illustrations (open-source content; <img> tags can't send headers).
_OPEN_PATHS = ("/api/health", "/api/exercise-images")


@app.middleware("http")
async def auth_guard(request: Request, call_next):
    if (
        settings.app_password
        and request.url.path.startswith("/api")
        and not request.url.path.startswith(_OPEN_PATHS)
        and request.method != "OPTIONS"
    ):
        supplied = request.headers.get("x-app-key") or request.query_params.get("key")
        if supplied != settings.app_password:
            return JSONResponse({"detail": "unauthorized"}, status_code=401)
    return await call_next(request)


@app.get("/api/health")
async def health():
    from app.db import get_pool

    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
    except Exception as exc:
        return JSONResponse(
            {"ok": False, "db": False, "detail": str(exc)[:200]},
            status_code=503,
        )
    return {"ok": True, "db": True}

# Self-hosted form illustrations (free-exercise-db) — start/end frames per lift.
_MEDIA_IMAGES = Path(__file__).parent.parent / "exercise_media" / "images"
if _MEDIA_IMAGES.exists():
    app.mount("/api/exercise-images", StaticFiles(directory=_MEDIA_IMAGES), name="exercise-images")


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


class ChatIn(BaseModel):
    message: str
    chat_id: str | None = None
    images: list[str] = []  # data URLs (physique photos)


@app.post("/api/chat")
async def chat(body: ChatIn, request: Request):
    agent = request.app.state.agent
    user_id = await tools.get_or_create_user()
    chat_id = body.chat_id or await tools.create_chat(user_id)
    await tools.maybe_title_chat(chat_id, body.message)
    config = {"configurable": {"thread_id": f"{user_id}:{chat_id}"}}

    content: str | list = body.message
    if body.images:
        content = [{"type": "text", "text": body.message or "Here are my physique photos."}]
        content += [{"type": "image_url", "image_url": {"url": u}} for u in body.images]

    async def stream():
        program_id = None
        sent_any = False
        final_text = ""
        try:
            async for mode, payload in agent.astream(
                {"messages": [{"role": "user", "content": content}], "user_id": user_id},
                config=config,
                stream_mode=["messages", "values"],
            ):
                if mode == "messages":
                    chunk, meta = payload
                    if meta.get("langgraph_node") == "act" and (text := _text(chunk.content)):
                        sent_any = True
                        yield f"data: {json.dumps({'type': 'token', 'text': text})}\n\n"
                else:  # values — snapshot of full state
                    program_id = payload.get("program_id") or program_id
                    if msgs := payload.get("messages"):
                        last = msgs[-1]
                        if getattr(last, "type", "") == "ai":
                            final_text = _text(last.content)
            # Non-streamed replies (e.g. the program ack is appended state, not
            # LLM tokens) — deliver the final assistant message in one piece.
            if not sent_any and final_text:
                yield f"data: {json.dumps({'type': 'token', 'text': final_text})}\n\n"
        except Exception as e:  # surface upstream failures (API, DB) to the client
            yield f"data: {json.dumps({'type': 'error', 'text': str(e)[:300]})}\n\n"
        done = {"type": "done", "chat_id": chat_id}
        if program_id:
            done["program_id"] = program_id
        yield f"data: {json.dumps(done)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


# ===== Chats =====

@app.post("/api/chats")
async def new_chat():
    user_id = await tools.get_or_create_user()
    return {"id": await tools.create_chat(user_id)}


@app.get("/api/chats")
async def chats_index():
    user_id = await tools.get_or_create_user()
    return await tools.list_chats(user_id)


@app.get("/api/chats/{chat_id}/messages")
async def chat_messages(chat_id: str, request: Request):
    user_id = await tools.get_or_create_user()
    snap = await request.app.state.agent.aget_state(
        {"configurable": {"thread_id": f"{user_id}:{chat_id}"}}
    )
    out = []
    for m in (snap.values or {}).get("messages", []):
        role = getattr(m, "type", "")
        if role not in ("human", "ai"):
            continue
        text = _text(m.content)
        if role == "human" and isinstance(m.content, list):
            n = sum(1 for b in m.content if isinstance(b, dict) and b.get("type") == "image_url")
            if n:
                text = f"📷 {n} photo{'s' if n > 1 else ''} — {text}"
        if text:
            out.append({"role": "user" if role == "human" else "assistant", "text": text})
    return out


# ===== Today's Workout (living plan, one-tap + voice logging) =====

@app.get("/api/today")
async def today(travel: str | None = None):
    user_id = await tools.get_or_create_user()
    if travel:
        from app.coaching.travel import travel_day
        from app.exercises.resolver import media_for
        from app.coaching.swaps import form_cue_for

        day = travel_day(travel)
        for ex in day["exercises"]:
            m = media_for(ex["exercise"])
            ex["image_urls"] = m["image_urls"] if m else []
            ex["form_cue"] = form_cue_for(ex["exercise"])
        return day
    day = await tools.get_today(user_id)
    if not day:
        return {"active": False}
    return {"active": True, **day}


class LogSetIn(BaseModel):
    program_id: str
    day_index: int
    slot_index: int
    exercise: str
    weight_lbs: float | None = None
    reps: int | None = None
    rir: float | None = None


@app.post("/api/today/log-set")
async def today_log_set(body: LogSetIn):
    user_id = await tools.get_or_create_user()
    result = await tools.log_today_set(
        user_id, body.program_id, body.day_index, body.slot_index, body.exercise,
        body.weight_lbs, body.reps, body.rir,
    )
    if result["is_pr"]:
        await notify(
            user_id, "🎉 New PR!",
            f"{body.exercise}: {body.weight_lbs}×{body.reps} — best yet.",
        )
    return result


class VoiceLogIn(BaseModel):
    text: str
    program_id: str
    day_index: int
    exercise_names: list[str]


@app.post("/api/today/log-voice")
async def today_log_voice(body: VoiceLogIn):
    user_id = await tools.get_or_create_user()
    try:
        parsed = await parse_voice_set(body.text, body.exercise_names)
    except Exception as e:
        raise HTTPException(503, f"couldn't parse that right now: {str(e)[:150]}") from e
    if not parsed.exercise:
        return {"matched": False, "heard": body.text}
    slot = await tools.resolve_open_slot(
        user_id, body.program_id, body.day_index, parsed.exercise, parsed.weight_lbs
    )
    result = await tools.log_today_set(
        user_id, body.program_id, body.day_index, slot, parsed.exercise,
        parsed.weight_lbs, parsed.reps, parsed.rir,
    )
    if result["is_pr"]:
        await notify(
            user_id, "🎉 New PR!",
            f"{parsed.exercise}: {parsed.weight_lbs}×{parsed.reps} — best yet.",
        )
    return {"matched": True, "parsed": parsed.model_dump(), **result}


class FinishTodayIn(BaseModel):
    program_id: str
    day_index: int
    session_rpe: float | None = None


@app.post("/api/today/finish")
async def today_finish(body: FinishTodayIn):
    user_id = await tools.get_or_create_user()
    return await tools.finish_today(user_id, body.program_id, body.day_index, body.session_rpe)


class CatchUpIn(BaseModel):
    program_id: str
    action: str  # resume | repeat_last | light_makeup


@app.post("/api/today/catch-up")
async def today_catch_up(body: CatchUpIn):
    if body.action not in ("resume", "repeat_last", "light_makeup"):
        raise HTTPException(400, "action must be resume | repeat_last | light_makeup")
    user_id = await tools.get_or_create_user()
    return await tools.apply_catch_up(user_id, body.program_id, body.action)


class SwapIn(BaseModel):
    program_id: str
    day_index: int
    slot_index: int
    new_exercise: str


@app.post("/api/today/swap")
async def today_swap(body: SwapIn):
    user_id = await tools.get_or_create_user()
    return await tools.swap_today_exercise(
        user_id, body.program_id, body.day_index, body.slot_index, body.new_exercise,
    )


class CheckinIn(BaseModel):
    sleep_h: float | None = None
    soreness_0_10: int | None = None
    stress_0_10: int | None = None
    motivation_0_10: int | None = None
    notes: str | None = None


@app.post("/api/today/checkin")
async def today_checkin(body: CheckinIn):
    """Subjective pre-session readiness — drives Today adaptation."""
    user_id = await tools.get_or_create_user()
    entry = body.model_dump(exclude_none=True)
    if not entry:
        raise HTTPException(400, "provide at least one readiness field")
    await tools.upsert_readiness(user_id, entry)
    day = await tools.get_today(user_id)
    return {"ok": True, "adaptation": (day or {}).get("adaptation"), "today": day}


@app.get("/api/coach/weekly-review")
async def weekly_review():
    from app.coaching.debrief import weekly_review_payload

    user_id = await tools.get_or_create_user()
    profile = await tools.get_latest_profile(user_id)
    readiness = await tools.get_recent_readiness(user_id, days=14)
    load = await tools.get_load_summary(user_id)
    prs = await tools.recent_prs(user_id, days=14)
    return weekly_review_payload(profile, readiness, load, [], prs)


# ===== Readiness (HealthKit sync) =====

class ReadinessIn(BaseModel):
    sleep_h: float | None = None
    hrv_ms: float | None = None
    resting_hr: int | None = None


@app.post("/api/readiness")
async def post_readiness(body: ReadinessIn):
    user_id = await tools.get_or_create_user()
    metrics = body.model_dump(exclude_none=True)
    if not metrics:
        raise HTTPException(400, "no readiness metrics provided")
    return await tools.store_health_readiness(user_id, metrics)


@app.get("/api/readiness/today")
async def readiness_today():
    user_id = await tools.get_or_create_user()
    recent = await tools.get_recent_readiness(user_id, days=1)
    return recent[0] if recent else {}


# ===== Push notifications =====

@app.get("/api/push/vapid-public-key")
async def vapid_public_key():
    return {"key": settings.vapid_public_key}


class PushSubscribeIn(BaseModel):
    subscription: dict


@app.post("/api/push/subscribe")
async def push_subscribe(body: PushSubscribeIn):
    user_id = await tools.get_or_create_user()
    await tools.save_push_subscription(user_id, body.subscription)
    return {"ok": True}


# ===== Profile (settings page) =====

class ProfilePatch(BaseModel):
    patch: dict


@app.patch("/api/profile")
async def patch_profile(body: ProfilePatch):
    user_id = await tools.get_or_create_user()
    merged = await tools.apply_profile_patch(user_id, body.patch, updated_by="user")
    return {"profile": merged}


# ===== Plan template gallery =====

@app.get("/api/templates")
async def templates():
    from app.exercises.resolver import media_for
    from app.plan_templates import TEMPLATES

    out = []
    for t in TEMPLATES:
        t = json.loads(json.dumps(t))  # deep copy
        t.setdefault("source_type", "book")
        for day in t["days"]:
            for ex in day["exercises"]:
                m = media_for(ex["name"])
                ex["image_urls"] = m["image_urls"] if m else []
        out.append(t)
    return out


class ActivateTemplateIn(BaseModel):
    template_id: str


@app.post("/api/templates/activate")
async def activate_template(body: ActivateTemplateIn):
    """One-tap: turn a gallery plan into the athlete's active program."""
    from app.plan_activate import get_template, suggest_nutrition, template_to_workout_plan

    user_id = await tools.get_or_create_user()
    t = get_template(body.template_id)
    if not t:
        raise HTTPException(404, "template not found")
    profile = await tools.get_latest_profile(user_id)
    plan = template_to_workout_plan(t, profile.get("name"))
    bw = profile.get("bodyweight_lbs")
    nutrition = suggest_nutrition(float(bw) if bw else None, t["goal"])
    if nutrition:
        plan.nutrition = nutrition
        await tools.apply_profile_patch(user_id, {
            "nutrition_targets": nutrition.model_dump(),
            "goal_mode": t["goal"] if t["goal"] != "general" else profile.get("goal_mode"),
        })
    # Drop the placeholder citation so PDF/UI don't claim a fake chunk_id
    plan.citations = []
    pid = await tools.save_program(user_id, plan)
    # Reset progress to day 0 for the new program
    await tools.get_or_init_progress(user_id, pid)
    return {"ok": True, "program_id": pid, "name": plan.program_name}


class OnboardingIn(BaseModel):
    name: str
    goal_mode: str = "general"
    schedule: str | None = None
    equipment: str | None = None
    bodyweight_lbs: float | None = None
    lifts_1rm: dict | None = None
    template_id: str | None = None


@app.post("/api/onboarding")
async def onboarding(body: OnboardingIn):
    """First-run setup: profile + optional starter plan activation."""
    from app.plan_activate import get_template, suggest_nutrition, template_to_workout_plan

    user_id = await tools.get_or_create_user()
    patch: dict = {
        "name": body.name.strip(),
        "goal_mode": body.goal_mode,
        "onboarded": True,
        "onboarded_at": __import__("datetime").date.today().isoformat(),
    }
    if body.schedule:
        patch["schedule"] = body.schedule
    if body.equipment:
        patch["equipment"] = body.equipment
    if body.bodyweight_lbs:
        patch["bodyweight_lbs"] = body.bodyweight_lbs
    if body.lifts_1rm:
        patch["lifts_1rm"] = {k: float(v) for k, v in body.lifts_1rm.items() if v}
    goals_map = {
        "athleticism": "Athleticism — power, vertical, court transfer",
        "strength": "Get stronger on the big lifts",
        "hypertrophy": "Build muscle with honest volume",
        "recomposition": "Get stronger and sharper",
        "general": "Stay capable and consistent",
    }
    patch["goals"] = goals_map.get(body.goal_mode, body.goal_mode)
    await tools.apply_profile_patch(user_id, patch, updated_by="onboarding")

    program_id = None
    if body.template_id:
        t = get_template(body.template_id)
        if not t:
            raise HTTPException(404, "template not found")
        plan = template_to_workout_plan(t, body.name.strip())
        nutrition = suggest_nutrition(body.bodyweight_lbs, body.goal_mode)
        if nutrition:
            plan.nutrition = nutrition
            await tools.apply_profile_patch(user_id, {"nutrition_targets": nutrition.model_dump()})
        plan.citations = []
        program_id = await tools.save_program(user_id, plan)
        await tools.get_or_init_progress(user_id, program_id)

    return {"ok": True, "program_id": program_id}


class IngestIn(BaseModel):
    path: str
    title: str
    author: str | None = None


@app.post("/api/ingest")
async def ingest(body: IngestIn):
    pdf = Path(body.path).expanduser()
    if not pdf.exists():
        raise HTTPException(404, f"file not found: {pdf}")
    doc_id = await ingest_pdf(pdf, body.title, body.author)
    return {"document_id": doc_id}


@app.get("/api/programs/{program_id}/pdf")
async def program_pdf(program_id: str):
    prog = await tools.get_program(program_id)
    if not prog:
        raise HTTPException(404, "program not found")
    pdf = render_program_pdf(prog["plan"], prog["created_at"])
    # ASCII-only: HTTP headers are latin-1, program names may have em-dashes etc.
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", prog["plan"]["program_name"]).strip("-").lower() or "program"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{name}.pdf"'},
    )


@app.get("/api/exercises/{name}/media")
async def exercise_media(name: str):
    """Form media for one exercise: two frame URLs (UI flips them = GIF feel)."""
    from app.exercises.resolver import media_for

    m = media_for(name)
    if not m:
        raise HTTPException(404, f"no form media matched for {name!r}")
    return {k: m[k] for k in ("matched", "image_urls", "instructions", "primary_muscles")}


@app.get("/api/dashboard")
async def dashboard():
    user_id = await tools.get_or_create_user()
    return {
        "profile": await tools.get_latest_profile(user_id),
        "readiness": await tools.get_recent_readiness(user_id),
        "load": await tools.get_load_summary(user_id),
        "programs": await tools.list_programs(user_id),
    }


@app.get("/api/warmup")
async def warmup_preview(weight_lbs: float, exercise: str = "", set_type: str = "straight"):
    """Preview a warm-up ramp for a working weight (used when the athlete edits load)."""
    from app.coaching.warmup import warmup_ramp

    if weight_lbs <= 0:
        raise HTTPException(400, "weight_lbs must be positive")
    return {
        "working_lbs": weight_lbs,
        "warmup_sets": warmup_ramp(weight_lbs, exercise=exercise, set_type=set_type),
    }


# Production: serve the built frontend from the same process (no Vite proxy).
# Mounted last so /api routes take precedence. Absent in local dev — harmless.
_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")
