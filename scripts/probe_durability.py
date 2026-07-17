"""Prove conversation memory survives a restart — no LLM calls.

Writes messages through the compiled graph's checkpointer, then reopens a
BRAND-NEW saver connection (what a process restart looks like) and reads
them back. If they're there, memory is durable in Postgres, not in RAM.
"""

import asyncio

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agent.graph import build_graph
from app.config import settings

CFG = {"configurable": {"thread_id": "durability-probe"}}


async def main() -> None:
    # Session 1: write state through the checkpointer.
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        await saver.setup()
        agent = build_graph(saver)
        await agent.aupdate_state(
            CFG, {"messages": [HumanMessage(content="my favorite lift is the front squat")]}
        )
    print("session 1: wrote 1 message, connection closed")

    # Session 2: fresh connection == process restart.
    async with AsyncPostgresSaver.from_conn_string(settings.database_url) as saver:
        agent = build_graph(saver)
        snap = await agent.aget_state(CFG)
        msgs = snap.values.get("messages", [])
        print(f"session 2 (after 'restart'): read {len(msgs)} message(s)")
        for m in msgs:
            print("   →", m.content)
        assert msgs and "front squat" in msgs[0].content, "durability FAILED"
        print("✓ DURABLE — conversation survived the reconnect")


if __name__ == "__main__":
    asyncio.run(main())
