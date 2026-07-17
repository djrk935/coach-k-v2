"""The decision loop: route → load_state → (retrieve) → act → update_memory."""

from langchain_anthropic import ChatAnthropic
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent import prompts, tools
from app.agent.state import AgentState
from app.config import settings
from app.retrieval.search import format_hits_for_prompt, hybrid_search
from app.schemas import MemoryDelta, WorkoutPlan

_llm = ChatAnthropic(
    model=settings.chat_model, api_key=settings.anthropic_api_key, max_tokens=8192
)
_fast = ChatAnthropic(
    model=settings.fast_model, api_key=settings.anthropic_api_key, max_tokens=2048
)

_INTENTS = {"program_request", "log", "coaching_qa", "checkin"}


def _text(content) -> str:
    """Anthropic content can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content if isinstance(b, dict))


async def route(state: AgentState) -> dict:
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

    if state["intent"] == "program_request":
        structured = _llm.with_structured_output(WorkoutPlan)
        plan: WorkoutPlan = await structured.ainvoke(
            [
                {"role": "system", "content": prompts.PROGRAM_SYSTEM},
                {"role": "system", "content": ctx},
                *state["messages"],
            ]
        )
        # Never let an invented citation through: keep only retrieved chunk ids.
        valid = set(state.get("retrieved_ids", []))
        plan.citations = [c for c in plan.citations if c.chunk_id in valid]
        program_id = await tools.save_program(state["user_id"], plan)
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
                {"role": "system", "content": prompts.COACH_SYSTEM},
                {"role": "system", "content": ctx},
                *state["messages"],
                {
                    "role": "user",
                    "content": f"[system: persisted this turn → {summary}. "
                    "Acknowledge like a coach — brief, note any PRs or red flags.]",
                },
            ]
        )
        return {"messages": [res]}

    # coaching_qa / checkin — grounded conversational reply (streams)
    res = await _llm.ainvoke(
        [
            {"role": "system", "content": prompts.COACH_SYSTEM},
            {"role": "system", "content": ctx},
            *state["messages"],
        ]
    )
    return {"messages": [res]}


async def update_memory(state: AgentState) -> dict:
    if state["intent"] == "log":
        return {}  # already persisted in act()
    structured = _fast.with_structured_output(MemoryDelta)
    delta: MemoryDelta = await structured.ainvoke(
        [
            {"role": "system", "content": prompts.MEMORY_EXTRACT},
            {"role": "system", "content": "KNOWN PROFILE:\n" + str(state["profile"])},
            *state["messages"][-2:],
        ]
    )
    await tools.apply_memory_delta(state["user_id"], delta)
    return {}


def _needs_sources(state: AgentState) -> str:
    return "retrieve" if state["intent"] in ("program_request", "coaching_qa") else "act"


def build_graph():
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
    # MemorySaver keeps per-user chat history across turns (thread_id = user_id).
    return g.compile(checkpointer=MemorySaver())


agent = build_graph()
