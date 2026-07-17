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
from app.agent.graph import build_graph
from app.artifacts.renderer import render_program_pdf
from app.config import settings
from app.db import close_pool
from app.ingestion.pipeline import ingest_pdf


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Durable per-user chat memory: the Postgres saver survives restarts, so
    # Coach K resumes a conversation mid-thread instead of forgetting it.
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        await saver.setup()  # idempotent: creates checkpoint tables if absent
        app.state.agent = build_graph(saver)
        yield
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
    return {"ok": True}

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
        for day in t["days"]:
            for ex in day["exercises"]:
                m = media_for(ex["name"])
                ex["image_urls"] = m["image_urls"] if m else []
        out.append(t)
    return out


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


# Production: serve the built frontend from the same process (no Vite proxy).
# Mounted last so /api routes take precedence. Absent in local dev — harmless.
_FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=_FRONTEND_DIST, html=True), name="frontend")
