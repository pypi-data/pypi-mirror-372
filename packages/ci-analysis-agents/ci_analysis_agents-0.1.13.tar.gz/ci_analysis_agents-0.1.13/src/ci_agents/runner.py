import json
import sys
import logging
import asyncio

from agents import Runner

from ci_agents.context_manage import conclude_ai_response
from ci_agents.hub_agent import HubAgentFactory
from ci_agents.types import AnalysisContext, LastAnalysisResult, AnalysisResult
from ci_agents.log_config import configure_root_logger, logger, wait_for_background_logging
from hooks.run_hook_log import global_run_hook
from langfuse.langfuse_decorate import langfuse_task
from agents.mcp import MCPServerSse

configure_root_logger()


@langfuse_task
async def analyze_failure(analysis_context: AnalysisContext) -> AnalysisResult:
    """
    Analyze the failure logs and return the analysis result.
    """
    logger.info("Starting failure analysis")
    server = MCPServerSse(
        name="mcp-ci-tools",
        params={"url": "http://aqa01-i01-ocr01.int.rclabenv.com:8003/sse"}
    )
    async with server:  # Use the built-in async context manager from MCPServerSse
        hub_agent_factory = HubAgentFactory(mcp_server=server)
        hub_agent = hub_agent_factory.get_agent()
        try:
            result = await asyncio.wait_for(
                Runner.run(
                    starting_agent=hub_agent,
                    input="Can you analyze the root cause of the CI failure with using the tools",
                    context=analysis_context,
                    hooks=global_run_hook
                ),
                timeout=120.0
            )
        except asyncio.TimeoutError:
            logger.error("Runner.run timed out after 120 seconds")
            raise
        except Exception as e:
            logger.error(f"Exception in Runner.run: {e}")
            raise
        logger.info(f"Hub agent run completed, starting to process the result")
        last_agent_response: LastAnalysisResult = result.final_output
        final_response = conclude_ai_response(last_agent_response, analysis_context)
        logger.info(f"Failure analysis completed. With failure type: {type(last_agent_response.failure_type)}; Summary hook events: {global_run_hook.run_events}")
        await wait_for_background_logging()
        return final_response

#
# async def analyze_failure_parallel(analysis_context: AnalysisContext) -> AIResponse:
#     """
#     Analyze failure using both lab agent and hub agent in sequence.
#     """
#     logger.info("Starting parallel failure analysis")
#     hub_agent_factory = await HubAgentFactory.create()
#
#     hub_agent = hub_agent_factory.get_agent()
#     lab_agent = LabAgentFactory().get_agent()
#
#     logger.info("Running lab agent analysis")
#     lab_result = await Runner.run(
#         starting_agent=lab_agent,
#         input="Can you analyze if the root cause of the CI failure is caused by lab environment issue",
#         context=analysis_context,
#         hooks=global_run_hook
#     )
#
#     logger.info("Running hub agent analysis with lab agent results")
#     result = await Runner.run(
#         starting_agent=hub_agent,
#         input=f"Can you analyze the root cause of the CI failure with the context and the result from lab agent {ItemHelpers.text_message_outputs(lab_result.new_items)}",
#         context=analysis_context,
#         hooks=global_run_hook
#     )
#
#     # Print event counts as DEBUG level
#     logger.debug(f"Run hook events: {global_run_hook.run_events}")
#     logger.debug(f"Agent hook events: {global_log_hook.events}")
#
#     logger.info("Parallel failure analysis completed")
#     return result.final_output
