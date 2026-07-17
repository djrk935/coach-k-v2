from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    user_id: str
    intent: str                 # program_request | log | coaching_qa | checkin
    profile: dict               # latest athlete model
    readiness: list[dict]       # 14-day window (trend reasoning)
    load: dict                  # ACWR + session counts
    sources: str                # formatted RAG hits (citation-ready)
    retrieved_ids: list[str]    # valid chunk ids for citation validation
    plan: dict                  # emitted WorkoutPlan (program_request only)
    program_id: str             # saved program row id
