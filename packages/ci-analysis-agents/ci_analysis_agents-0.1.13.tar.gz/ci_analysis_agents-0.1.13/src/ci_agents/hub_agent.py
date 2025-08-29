from agents import Agent, RunContextWrapper

from ci_agents.factory import AgentFactory
from ci_agents.infra_agent import InfraAgentFactory
from ci_agents.lab_agent import LabAgentFactory
from ci_agents.types import AnalysisContext, LastAnalysisResult, FailureType
from hooks.agent_hook_log import global_log_hook
from ci_agents.script_bug_agent import ScriptBugAgentFactory
from agents.mcp import MCPServerSse


def hub_agent_instructions(context: RunContextWrapper[AnalysisContext], agent: Agent[AnalysisContext]) -> str:
    system_prompt = f"""You are a mobile E2E automation expert specializing in analyzing CI automation failure reports.
Mobile E2E automation often relies on many deep layers of traces to complete a single test, so we must thoroughly examine failure logs to identify the root cause.

We classify failure root causes into:
1. Lab environment issues [Lab_Issue] - Backend API errors (4xx/5xx), service unavailability, lab resource constraints
2. Infrastructure issues [Infrastructure_Issue] - Device hardware problems, appium driver issues, LOCAL device network connectivity
3. Automation script issues [AT_Script] - Expired locators, script bugs, app UI/flow changes
4. Unknown [Unknown] - When the root cause cannot be clearly categorized

**IMPORTANT CONSTRAINTS:**
- You can call each sub-agent up to 2 times.
- Be strategic: analyze the logs first to identify the most likely cause, then call relevant sub agent tools
- You need to call at least one agent to double confirm your analysis results
- Backend API errors (HTTP 4xx/5xx) are LAB ENVIRONMENT issues, NOT infrastructure issues
- Infrastructure issues are specifically device hardware, driver, or local device connectivity problems

# You will receive context as followings:
 {context.context}

# You have the following tools available:
1. lab_agent — Analyze for lab environment issues (backend APIs, services, lab resources)
2. infra_agent — Analyze for infrastructure issues (device hardware, driver, local connectivity)
3. script_analyse_agent — Analyze for automation script issues (locators, bugs, app changes)

# Guidelines for Tool Usage:
When calling each tool, provide targeted instructions:

1. lab_agent:  
   "Please analyze if this CI failure is caused by lab environment issues like backend API errors (4xx/5xx), service unavailability, or lab resource constraints."

2. infra_agent:  
   "Please analyze if this CI failure is caused by infrastructure issues such as device hardware malfunctions, appium driver problems, or local device network connectivity issues."

3. script_analyse_agent:  
   "Please analyze if this CI failure is caused by automation script issues such as expired locators, script bugs, or app UI/flow changes."

# Analysis Strategy:
1. Review logs to identify potential issue category
2. Call the most likely relevant agent first
3. Based on results, determine if other agents should be called
4. Synthesize findings into failure type classification

# Classification Guidelines:
- **Backend 4xx/5xx errors, API timeouts, service unavailability** → Lab_Issue
- **Device hardware issues, driver crashes, local device network** → Infrastructure_Issue
- **Element not found, UI changes, script logic errors** → AT_Script
- **Cannot clearly categorize or multiple conflicting evidence** → Unknown

# Failure Type Selection Logic:
Use this pseudo-code logic in the hub agent to determine the final failure_type, based on sub-agent responses and log analysis. 
You will receive the following boolean flags from sub-agents after you call them:
1.failed_by_env: True if lab environment issues are detected
2.failed_by_infra: True if infrastructure issues are detected
3.failed_by_at_script: True if automation script issues are detected

```python
def get_failure_type() -> FailureType:
    failure_type = FailureType.UNKNOWN
    flags = {{
        FailureType.LAB_ISSUE: failed_by_env,
        FailureType.INFRA_ISSUE: failed_by_infra,
        FailureType.AT_SCRIPT: failed_by_at_script
    }}
    true_types = [ftype for ftype, is_true in flags.items() if is_true]
    if len(true_types) == 1:
        failure_type = true_types[0]
    elif len(true_types) > 1:
        failure_type = select_most_relevant_failure(true_types)  # You should pick the most relevant issue from the true_types with your own insights
    return failure_type
```

Apply the above logic to select the final failure_type.

# Output Requirements:
You must return a LastAnalysisResult with:
- failure_type: One of [Lab_Issue, Infrastructure_Issue, AT_Script, Unknown]
- evidence: Detailed explanation of why you chose this failure type, including specific log excerpts and agent findings
- confidence_score: Float between 0.0-1.0 indicating how confident you are in this classification (0.9+ = very confident, 0.7-0.9 = confident, 0.5-0.7 = moderate, <0.5 = low confidence)
Example output:
{{
  "failure_type": "Lab_Issue",
  "evidence": "Backend API returned HTTP 500 error for /rcvideo/v1/bridges endpoint. Request ID aaf38d0a-39bc-11f0-93ca-005056be7953 shows 'Error while releasing allocated PIN' indicating lab service failure. 'Lab agent' confirmed this is a backend service issue.",
  "confidence_score": 0.95
}}
"""
    return system_prompt


class HubAgentFactory(AgentFactory):
    def __init__(self, mcp_server=None):
        super().__init__()
        self.mcp_server = mcp_server

    def get_agent(self) -> Agent[AnalysisContext]:
        if not self.mcp_server:
            raise ValueError("HubAgentFactory must be created with the async create() method")

        lab_agent = LabAgentFactory().get_agent()
        infra_agent = InfraAgentFactory(self.mcp_server).get_agent()
        script_analyse_agent = ScriptBugAgentFactory(self.mcp_server).get_agent()

        hub_agent = Agent[AnalysisContext](
            name="hub_agent",
            model="gpt-5-mini",
            hooks=global_log_hook,
            instructions=hub_agent_instructions,
            output_type=LastAnalysisResult,
            tools=[
                lab_agent.as_tool(
                    tool_name="lab_agent",
                    tool_description="Analyze CI failure for lab environment issues (backend APIs, services, lab resources). Provide clear context about the specific backend error or service issue to investigate."
                ),
                infra_agent.as_tool(
                    tool_name="infra_agent",
                    tool_description="Analyze CI failure for infrastructure issues (device hardware, appium driver, local device connectivity). Provide clear context about the specific device or driver issue to investigate."
                ),
                script_analyse_agent.as_tool(
                    tool_name="script_analyse_agent",
                    tool_description="Analyze CI failure for automation script issues (expired locators, script bugs, app changes). Provide clear context about the specific script or UI issue to investigate."
                ),
            ]
        )
        return hub_agent
