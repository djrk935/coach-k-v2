"""FastAPI surface: SSE chat, ingestion, program PDFs, dashboard."""

import json
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from app.agent import tools
from app.agent.graph import agent
from app.artifacts.renderer import render_program_pdf
from app.db import close_pool
from app.ingestion.pipeline import ingest_pdf


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await close_pool()


app = FastAPI(title="Coach K v2", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


class ChatIn(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(body: ChatIn):
    user_id = await tools.get_or_create_user()
    config = {"configurable": {"thread_id": user_id}}

    async def stream():
        program_id = None
        sent_any = False
        final_text = ""
        try:
            async for mode, payload in agent.astream(
                {"messages": [{"role": "user", "content": body.message}], "user_id": user_id},
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
        done = {"type": "done", **({"program_id": program_id} if program_id else {})}
        yield f"data: {json.dumps(done)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


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


@app.get("/api/dashboard")
async def dashboard():
    user_id = await tools.get_or_create_user()
    return {
        "profile": await tools.get_latest_profile(user_id),
        "readiness": await tools.get_recent_readiness(user_id),
        "load": await tools.get_load_summary(user_id),
        "programs": await tools.list_programs(user_id),
    }
