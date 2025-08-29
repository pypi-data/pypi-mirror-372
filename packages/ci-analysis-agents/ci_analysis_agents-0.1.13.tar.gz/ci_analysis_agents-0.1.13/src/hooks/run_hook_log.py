from collections import defaultdict

from agents import RunHooks, RunContextWrapper, TContext, Agent, Tool
from typing import Any
from ci_agents.log_config import logger


class RunHooksForLog(RunHooks):
    def __init__(self):
        self.run_events: dict[str, int] = defaultdict(int)

    async def on_agent_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext]) -> None:
        logger.info(f"[RUN-HOOK] Agent {agent.name} starting in run")
        self.run_events["agent_start"] += 1

    async def on_agent_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], output: Any) -> None:
        logger.info(f"[RUN-HOOK] Agent {agent.name} completed in run")
        self.run_events["agent_end"] += 1

    async def on_handoff(self, context: RunContextWrapper[TContext], from_agent: Agent[TContext], to_agent: Agent[TContext]) -> None:
        logger.info(f"[RUN-HOOK] Handoff from {from_agent.name} to {to_agent.name}")
        self.run_events["handoff"] += 1

    async def on_tool_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool) -> None:
        logger.info(f"[RUN-HOOK] Tool {tool.name} starting for agent {agent.name}")
        self.run_events["tool_start"] += 1

    async def on_tool_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool, result: str) -> None:
        logger.info(f"[RUN-HOOK] Tool {tool.name} completed for agent {agent.name}")
        self.run_events["tool_end"] += 1


global_run_hook = RunHooksForLog()
