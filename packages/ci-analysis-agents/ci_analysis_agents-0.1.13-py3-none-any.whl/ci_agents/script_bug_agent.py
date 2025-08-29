import logging
from agents import RunContextWrapper, Agent, function_tool
import subprocess

import openai

from ci_agents.factory import AgentFactory
from ci_agents.types import AnalysisContext, ATScriptAIResponse
from hooks.agent_hook_log import global_log_hook
from agents.mcp import MCPServer, MCPServerSse

logger = logging.getLogger("script_bug_agent")

@function_tool
def execute_terminal_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"execute terminal command failed: {e.stderr}"

import os
import tempfile
import requests

@function_tool
def attach_image_to_assistant_by_url(url: str) -> dict:
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        temp_file.close()
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        with open(temp_file_path, 'rb') as f:
            file = openai.files.create(
                file=f,
                purpose="assistants"
            )
        print(f"✅ file download and upload success, file_id: {file.id}")
        return {
            'asset_pointer': file.id,
            'content_type': 'image_asset_pointer',
            'height': 0,  # Placeholder, actual height not available
            'width': 0,  # Placeholder, actual width not available
            'size_bytes': os.path.getsize(temp_file_path),
            'use_case': 'multimodal',
        }
    
    except Exception as e:
        return f"file process failed: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"✅ delete temp file: {temp_file_path}")

def script_agent_instructions(context: RunContextWrapper[AnalysisContext], agent: Agent[AnalysisContext]) -> str:
    # failure_log = context.context.failure_log
    # failed_thread_log = context.context.failed_thread_log
    # • {failure_log} → Key error stack trace from the automation framework
    # • {failed_thread_log} → Detailed log of the failure event
    test_id = context.context.test_id
    project_id = 751
    system_prompt = f"""
    #Role:
    You are a mobile E2E automation expert specializing in analyzing CI automation failure reports.
    You are highly proficient in programming languages such as Java and Kotlin, and you are skilled with automation tools including Appium and Cucumber. 
    Your expertise lies in diagnosing whether a failure is caused by AT script issue.
    Please note that don't attribute everything to script issues，such device issue/network issue/third-party/test environment issue should be excluded.
    #Data Provided:
    You can call mcp server by test_id {test_id} to retrieve the failed case metadata. 
    #Note
    when use extract_image_file_from_url ,max_size =256

    #Analyse Steps:
     1.Load the failed test case metadata using testId={test_id}.
     2.Download the failed step screenshot image from case metadata and analyse it
     3.If need,get last successful case metadata, Then compare the failed and successful screenshot, focusing on UI elements, states, and transitions.
     4.You can search the code line by call get_file_contents with stacktrace info (Note:project id={project_id},file path start with "/src/") to find the exact code line that caused the failure.
     5.If you think it's about appium locator issue,you can download sourcenode.xml by curl command with grep what you want to find.
     6.Analyze the root cause using all available data:
         Relevant logs or stack trace (for Script Issue)
         Annotated screenshot diffs
    """
    requirement = """
    #Output Requirements:
    {
       "root_cause_insight": "Clearly explain the exact root cause of the failure.",
       "action_insight": {
          "code_line": "Extracted code line from the logs that caused the failure.",
        },
        “actionSuggestion": "Provide a clear action to fix the issue, such as updating locators, fixing code bugs, or adjusting test scripts.",
       "failed_by_at_script": "If test fail by AT script issue, please return true, otherwise false",
       "reason":"Describe the content of the failed and successful screenshots in detail, compare their differences, and analyze whether the differences are related to the case failure",
    }
    Notes:
    • "rootCauseInsight" should clearly explain the reason for the failure based on log analysis.
    • "actionSuggestion" should give a clear action to fix the issue.
    • Ensure the response is strictly in JSON format.

    ##Case 2: If the failure is NOT caused by an at script, return:
    {
      "root_cause_insight": "Explain why the failure is not due to the automation script issue. Provide your thought process and references.",
      "failed_by_at_script": false
    }
    """
    please_note = """
      #Important:
      • You MUST finish your analysis and produce a complete JSON response within 3 step.
      • Do NOT ask follow-up questions or request additional clarification.
      """
    return system_prompt + requirement


class ScriptBugAgentFactory(AgentFactory):

    def __init__(self, ci_mcp: MCPServer = None):
        super().__init__()
        self.ci_mcp = ci_mcp

    def get_agent(self) -> Agent[AnalysisContext]:
        if not self.ci_mcp:
            raise ValueError("MCPServer must be provided to ScriptBugAgentFactory")
        script_analyse_agent = Agent[AnalysisContext](
            name="script_analyse_agent",
            model="gpt-4o",
            instructions=script_agent_instructions,
            mcp_servers=[self.ci_mcp],
            output_type=ATScriptAIResponse,
            hooks=global_log_hook,
            tools=[execute_terminal_command],
        )
        return script_analyse_agent
