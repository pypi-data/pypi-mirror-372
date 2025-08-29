from collections import defaultdict
from typing import Any

from agents import AgentHooks, RunContextWrapper, TContext, Agent, Tool


class AgentHooksForContext(AgentHooks):
    def __init__(self):
        self.events: dict[str, int] = defaultdict(int)

    async def on_tool_start(
            self,
            context: RunContextWrapper[TContext],
            agent: Agent[TContext],
            tool: Tool,
    ) -> None:
        # todo needs to retrieve some data from the tool to set to context to be visible to the hub agent??  share context??
        self.events["on_tool_start"] += 1

    async def on_tool_end(
            self,
            context: RunContextWrapper[TContext],
            agent: Agent[TContext],
            tool: Tool,
            result: str,
    ) -> None:
        # todo needs to retrieve some data from the tool to set to context to be visible to the hub agent??
        self.events["on_tool_end"] += 1


agent_hook_for_context = AgentHooksForContext()
