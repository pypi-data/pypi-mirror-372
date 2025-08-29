from agents import RunContextWrapper, Agent, function_tool

from ci_agents.types import AnalysisContext, InfraIssueAIResponse
from hooks.agent_hook_log import global_log_hook


def infra_agent_instructions(context: RunContextWrapper[AnalysisContext], agent: Agent[AnalysisContext]) -> str:
    failure_log = context.context.failure_log
    failed_thread_log = context.context.failed_thread_log
    appium_log = context.context.appium_log
    system_prompt = f"""
    #Role:
    You are a mobile E2E automation expert specializing in analyzing CI automation failure reports. Your expertise lies in diagnosing whether a failure is caused by the infrastructure issues (e.g.device issue, driver issue).
    
    #Tasks:
    Your goal is to determine whether a CI test report failure is caused by infrastructure issue by analyzing logs
       
    #Data Provided:
    You will receive the following logs to aid in analysis:
    • {failure_log} → Key error stack trace from the automation framework
    • {failed_thread_log} → Detailed log of the failure event
    • {appium_log} (Optional) → appium logs related to the failure
    """
    return system_prompt


@function_tool
def dynamic_fetch_appium_log() -> str:
    """
    This function is a placeholder for the actual implementation of fetching the appium log.
    It should be replaced with the appropriate logic to retrieve the appium log as needed.
    """
    return "appium_log_placeholder-- working fine"


infra_fake_agent = Agent[AnalysisContext](
    name="infra_fake_agent",
    model="gpt-5-mini",
    instructions=infra_agent_instructions,
    output_type=InfraIssueAIResponse,
    hooks=global_log_hook,
    tools=[dynamic_fetch_appium_log]  # Add the dynamic tool to the agent
)
