from collections import defaultdict
from typing import Any

from agents import AgentHooks, RunContextWrapper, TContext, Agent, Tool

from ci_agents.log_config import logger
from ci_agents.context_manage import save_response_to_context


class AgentHooksForLog(AgentHooks):
    def __init__(self):
        self.events: dict[str, int] = defaultdict(int)

    def reset(self):
        self.events.clear()

    async def on_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext]) -> None:
        logger.info(f"[AGENT-HOOK] Agent {agent.name} on_start")
        logger.debug(f"Agent {agent.name} started with context: {context.context}")
        self.events["on_start"] += 1

    async def on_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], output: Any) -> None:
        logger.info(f"[AGENT-HOOK] Agent {agent.name} on_end")
        save_response_to_context(context.context, output)
        self.events["on_end"] += 1

    async def on_handoff(self, context: RunContextWrapper[TContext], agent: Agent[TContext], source: Agent[TContext]) -> None:
        logger.info(f"[AGENT-HOOK] Agent handoff from {source.name} to {agent.name}")
        self.events["on_handoff"] += 1

    async def on_tool_start(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool) -> None:
        logger.info(f"[AGENT-HOOK] Agent {agent.name} on_tool_start: {tool.name}")
        self.events["on_tool_start"] += 1

    async def on_tool_end(self, context: RunContextWrapper[TContext], agent: Agent[TContext], tool: Tool, result: str) -> None:
        logger.info(f"[AGENT-HOOK] Agent {agent.name} on_tool_end: {tool.name}")
        if "fetch_appium_log" in tool.name.lower() and hasattr(context.context, "appium_log"):
            logger.debug(f"[AGENT-HOOK] Adding appium_log to context...")
            context.context.appium_log = result
        self.events["on_tool_end"] += 1


# Create a single global instance that persists across runs
global_log_hook = AgentHooksForLog()
