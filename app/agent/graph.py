"""The decision loop: route → load_state → (retrieve) → act → update_memory."""

import json
from base64 import b64decode
from datetime import date
from pathlib import Path
from uuid import uuid4

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.agent import prompts, tools
from app.agent.state import AgentState
from app.config import settings
from app.retrieval.search import format_hits_for_prompt, hybrid_search
from app.schemas import MemoryDelta, PhysiqueAssessment, VoiceSetLog, WorkoutPlan

PHOTOS_DIR = Path(__file__).parent.parent.parent / "photos"

_llm = ChatAnthropic(
    model=settings.chat_model, api_key=settings.anthropic_api_key, max_tokens=8192
)
_fast = ChatAnthropic(
    model=settings.fast_model, api_key=settings.anthropic_api_key, max_tokens=2048
)

_INTENTS = {
    "program_request", "log", "coaching_qa", "checkin",
    "adapt_today", "deload", "review_block", "travel",
}


def _sys(text: str, cache: bool = False) -> dict:
    """A system message. When cache=True, mark it as an Anthropic prompt-cache
    breakpoint so repeat turns within the TTL re-read this prefix at ~10% cost
    instead of re-billing (and re-computing) the full tokens. We cache the two
    stable-within-a-session prefixes — the coach's system prompt and the
    athlete/context block — which is where nearly all the repeated tokens live."""
    if cache:
        return {"role": "system", "content": [
            {"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}
        ]}
    return {"role": "system", "content": text}


async def parse_voice_set(text: str, exercise_names: list[str]) -> VoiceSetLog:
    """One-liner ('bench 225 for 5 at RPE 8') -> structured set. Used by the
    Today view's tap-or-speak logging — no full agent turn, just extraction."""
    structured = _fast.with_structured_output(VoiceSetLog)
    return await structured.ainvoke([
        {
            "role": "system",
            "content": (
                "Extract a single logged set from this gym shorthand. "
                f"Match `exercise` verbatim to one of: {exercise_names}. "
                "If it doesn't clearly match any, leave exercise null. "
                "Weight is in pounds. Extract only what's stated — no guessing."
            ),
        },
        {"role": "user", "content": text},
    ])


async def run_form_check(
    user_id: str,
    exercise: str,
    images: list[str],
    note: str | None = None,
    form_cue: str | None = None,
) -> dict:
    """Vision form check from client-extracted video keyframes (data URLs)."""
    from app.schemas import FormCheckAssessment

    if not images:
        raise ValueError("at least one frame required")
    if len(images) > 6:
        raise ValueError("max 6 frames")

    PHOTOS_DIR.mkdir(exist_ok=True)
    form_dir = PHOTOS_DIR / "form-check"
    form_dir.mkdir(exist_ok=True)
    paths: list[str] = []
    for url in images:
        if not url.startswith("data:"):
            raise ValueError("images must be data URLs")
        header, _, b64 = url.partition(",")
        if not b64:
            raise ValueError("invalid data URL")
        ext = "png" if "png" in header else "jpg"
        p = form_dir / f"{date.today()}-{uuid4().hex[:8]}.{ext}"
        p.write_bytes(b64decode(b64))
        paths.append(str(p))

    cue_line = f"Known form cue for this lift: {form_cue}" if form_cue else ""
    note_line = f"Athlete note: {note}" if note else ""
    user_content: list[dict] = [
        {
            "type": "text",
            "text": (
                f"Exercise: {exercise}\n"
                f"{cue_line}\n{note_line}\n"
                "These images are sequential keyframes from one set. "
                "Assess technique for this lift."
            ).strip(),
        },
        *[{"type": "image_url", "image_url": {"url": u}} for u in images],
    ]

    structured = _llm.with_structured_output(FormCheckAssessment)
    a: FormCheckAssessment = await structured.ainvoke([
        _sys(prompts.FORM_CHECK_SYSTEM, cache=True),
        {"role": "user", "content": user_content},
    ])
    assessment = a.model_dump()
    await tools.save_form_check(user_id, exercise, paths, assessment, note)
    return {"ok": True, "exercise": exercise, "assessment": assessment, "frames": len(paths)}


def _text(content) -> str:
    """Anthropic content can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


def _image_blocks(content) -> list[dict]:
    if not isinstance(content, list):
        return []
    return [b for b in content if isinstance(b, dict) and b.get("type") == "image_url"]


async def route(state: AgentState) -> dict:
    # Photos attached → physique analysis, no classifier call needed.
    if _image_blocks(state["messages"][-1].content):
        return {"intent": "physique"}
    res = await _fast.ainvoke(
        [{"role": "system", "content": prompts.ROUTER}, state["messages"][-1]]
    )
    label = _text(res.content).strip().lower()
    return {"intent": label if label in _INTENTS else "coaching_qa"}


async def load_state(state: AgentState) -> dict:
    uid = state["user_id"]
    return {
        "profile": await tools.get_latest_profile(uid),
        "readiness": await tools.get_recent_readiness(uid),
        "load": await tools.get_load_summary(uid),
    }


async def retrieve(state: AgentState) -> dict:
    query = _text(state["messages"][-1].content)
    prefer = "table" if state["intent"] == "program_request" else None
    k = 12 if state["intent"] == "program_request" else 6
    hits = await hybrid_search(query, k=k, prefer_type=prefer)
    return {
        "sources": format_hits_for_prompt(hits),
        "retrieved_ids": [h["id"] for h in hits],
    }


async def act(state: AgentState) -> dict:
    ctx = tools.format_context(
        state["profile"], state["readiness"], state["load"], state.get("sources")
    )
    # Enrich context with living coaching signals when available.
    try:
        from app.coaching.adapt import adaptation_for
        from app.coaching.debrief import weekly_review_payload

        pain = await tools.active_pain_regions(state["user_id"], state["profile"] or {})
        today_ready = (state["readiness"] or [None])[0]
        adapt = adaptation_for(today_ready, state["load"], pain)
        ctx += "\n\nADAPTATION (system-computed for today):\n" + json.dumps(adapt, indent=1)
        if state["intent"] == "review_block":
            review = weekly_review_payload(
                state["profile"] or {},
                state["readiness"] or [],
                state["load"] or {},
                [],
                [],
            )
            ctx += "\n\nWEEKLY REVIEW DRAFT:\n" + review["message"]
    except Exception:
        pass

    if state["intent"] == "program_request":
        structured = _llm.with_structured_output(WorkoutPlan)
        plan: WorkoutPlan = await structured.ainvoke(
            [
                _sys(prompts.PROGRAM_SYSTEM, cache=True),
                _sys(ctx, cache=True),
                *state["messages"],
            ]
        )
        # Never let an invented citation through: keep only retrieved chunk ids.
        valid = set(state.get("retrieved_ids", []))
        plan.citations = [c for c in plan.citations if c.chunk_id in valid]
        program_id = await tools.save_program(state["user_id"], plan)
        await tools.get_or_init_progress(state["user_id"], program_id)
        # Persist nutrition targets onto profile for ongoing check-ins.
        if plan.nutrition:
            await tools.apply_profile_patch(state["user_id"], {
                "nutrition_targets": plan.nutrition.model_dump(),
            })
        ack = (
            f"**{plan.program_name}** is built — {plan.mesocycle_weeks} weeks, "
            f"{plan.periodization_model} periodization, grounded in "
            f"{len(plan.citations)} sources from your library.\n\n"
            f"{plan.scientific_rationale}\n\n"
            f"[Download the PDF](/api/programs/{program_id}/pdf)"
        )
        return {
            "plan": plan.model_dump(),
            "program_id": program_id,
            "messages": [{"role": "assistant", "content": ack}],
        }

    if state["intent"] == "physique":
        # 1. Persist the photos locally (private; gitignored dir).
        PHOTOS_DIR.mkdir(exist_ok=True)
        paths = []
        for block in _image_blocks(state["messages"][-1].content):
            header, _, b64 = block["image_url"]["url"].partition(",")
            ext = "png" if "png" in header else "jpg"
            p = PHOTOS_DIR / f"{date.today()}-{uuid4().hex[:8]}.{ext}"
            p.write_bytes(b64decode(b64))
            paths.append(str(p))

        # 2. Assess with vision + prior history for a real progress comparison.
        history = await tools.get_physique_history(state["user_id"])
        msgs = [
            _sys(prompts.PHYSIQUE_SYSTEM, cache=True),
            _sys(ctx, cache=True),
        ]
        if history:
            msgs.append({
                "role": "system",
                "content": "PRIOR ASSESSMENTS (newest first):\n" + json.dumps(history),
            })
        structured = _llm.with_structured_output(PhysiqueAssessment)
        a: PhysiqueAssessment = await structured.ainvoke([*msgs, *state["messages"]])

        # 3. Persist + fold into the profile so programming sees it.
        await tools.save_physique_assessment(state["user_id"], paths, a.model_dump())
        await tools.apply_profile_patch(state["user_id"], {"physique": {
            "last_assessed": str(date.today()),
            "estimated_bodyfat_range": a.estimated_bodyfat_range,
            "strong_points": a.strong_points,
            "lagging_points": a.lagging_points,
        }})

        lines = [a.overall, "", f"**Est. body fat:** {a.estimated_bodyfat_range}"]
        if a.strong_points:
            lines.append("**Standing out:** " + ", ".join(a.strong_points))
        if a.lagging_points:
            lines.append("**Priority targets:** " + ", ".join(a.lagging_points))
        if a.posture_notes:
            lines.append(f"**Posture:** {a.posture_notes}")
        if a.vs_previous:
            lines += ["", f"**Since last photos:** {a.vs_previous}"]
        lines += ["", a.training_implications]
        return {"messages": [{"role": "assistant", "content": "\n".join(lines)}]}

    if state["intent"] == "log":
        # Parse + persist FIRST so the ack reflects real results (PRs, flags).
        structured = _fast.with_structured_output(MemoryDelta)
        delta: MemoryDelta = await structured.ainvoke(
            [
                {"role": "system", "content": prompts.MEMORY_EXTRACT},
                {"role": "system", "content": "KNOWN PROFILE:\n" + str(state["profile"])},
                state["messages"][-1],
            ]
        )
        summary = await tools.apply_memory_delta(state["user_id"], delta)
        res = await _llm.ainvoke(
            [
                _sys(prompts.COACH_SYSTEM, cache=True),
                _sys(ctx, cache=True),
                *state["messages"],
                {
                    "role": "user",
                    "content": f"[system: persisted this turn → {summary}. "
                    "Acknowledge like a coach — brief, note any PRs or red flags.]",
                },
            ]
        )
        return {"messages": [res]}

    intent_system = {
        "adapt_today": prompts.ADAPT_SYSTEM,
        "deload": prompts.DELOAD_SYSTEM,
        "review_block": prompts.REVIEW_SYSTEM,
        "travel": prompts.TRAVEL_SYSTEM,
    }.get(state["intent"], prompts.COACH_SYSTEM)

    # coaching_qa / checkin / adapt / deload / review / travel
    res = await _llm.ainvoke(
        [
            _sys(intent_system, cache=True),
            _sys(ctx, cache=True),
            *state["messages"],
        ]
    )
    return {"messages": [res]}


async def update_memory(state: AgentState) -> dict:
    if state["intent"] in ("log", "physique"):
        return {}  # already persisted in act()
    try:
        structured = _fast.with_structured_output(MemoryDelta)
        delta: MemoryDelta = await structured.ainvoke(
            [
                {"role": "system", "content": prompts.MEMORY_EXTRACT},
                {"role": "system", "content": "KNOWN PROFILE:\n" + str(state["profile"])},
                *state["messages"][-2:],
            ]
        )
        await tools.apply_memory_delta(state["user_id"], delta)
    except Exception:
        # Never fail the user-facing turn on memory extraction / schema quirks.
        pass
    return {}


def _needs_sources(state: AgentState) -> str:
    return "retrieve" if state["intent"] in (
        "program_request", "coaching_qa", "adapt_today", "deload", "travel",
    ) else "act"


def build_graph(checkpointer: BaseCheckpointSaver | None = None):
    g = StateGraph(AgentState)
    g.add_node("route", route)
    g.add_node("load_state", load_state)
    g.add_node("retrieve", retrieve)
    g.add_node("act", act)
    g.add_node("update_memory", update_memory)

    g.add_edge(START, "route")
    g.add_edge("route", "load_state")
    g.add_conditional_edges("load_state", _needs_sources, {"retrieve": "retrieve", "act": "act"})
    g.add_edge("retrieve", "act")
    g.add_edge("act", "update_memory")
    g.add_edge("update_memory", END)
    # The checkpointer persists per-user chat history across turns (thread_id =
    # user_id). A Postgres saver (injected at startup) makes it survive restarts;
    # None keeps it in-memory for tests.
    return g.compile(checkpointer=checkpointer)
