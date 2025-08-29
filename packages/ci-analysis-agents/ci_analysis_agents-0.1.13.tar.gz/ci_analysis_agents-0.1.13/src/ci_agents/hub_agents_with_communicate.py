import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union

from agents import Agent, Runner, function_tool, trace, ItemHelpers, MessageOutputItem, ToolCallItem

@dataclass
class AnalysisContext:
    test_id: str
    logs: str = ""
    full_report: Dict[str, Any] = field(default_factory=dict)
    analysis_history: List[Dict[str, Any]] = field(default_factory=list)
    evidence_collected: List[str] = field(default_factory=list)

@dataclass
class AnalysisResult:
    root_cause: str
    confidence: int
    evidence: List[str]
    reasoning: str
    recommendations: List[str]

# Specialized agents to handle different aspects of analysis
def lab_agent_instructions() -> str:
    return """You analyze logs for lab environment issues like test environments, hardware resources, and connectivity.
    Look for patterns such as:
    - Connection timeouts to test environments
    - Resource exhaustion (memory, CPU)
    - Environment setup failures
    
    Return a detailed analysis in JSON format with:
    - is_lab_issue: boolean indicating if this is a lab issue
    - confidence: number from 0-100
    - evidence: list of specific log excerpts supporting your conclusion
    - reasoning: your step-by-step analysis process
    - recommendations: specific actions to resolve the issue
    """

def infra_agent_instructions() -> str:
    return """You analyze logs for infrastructure issues like devices, drivers, networks, and system components.
    Look for patterns such as:
    - Device connectivity failures
    - Driver crashes or errors
    - Network timeouts or failures
    - System component failures
    
    Return a detailed analysis in JSON format with:
    - is_infra_issue: boolean indicating if this is an infrastructure issue
    - confidence: number from 0-100
    - evidence: list of specific log excerpts supporting your conclusion
    - reasoning: your step-by-step analysis process
    - recommendations: specific actions to resolve the issue
    """

def script_agent_instructions() -> str:
    return """You analyze logs for automation script issues like locators, assertions, and test logic.
    Look for patterns such as:
    - Element not found errors
    - Assertion failures
    - Timing issues in scripts
    - Changes in app UI
    
    Return a detailed analysis in JSON format with:
    - is_script_issue: boolean indicating if this is a script issue
    - confidence: number from 0-100
    - evidence: list of specific log excerpts supporting your conclusion
    - reasoning: your step-by-step analysis process
    - recommendations: specific actions to resolve the issue
    """

# Context-aware orchestrator agent
def orchestrator_instructions() -> str:
    return """You are a CI analysis orchestrator. Your job is to:
    
    1. Review the current analysis context
    2. Determine which specialized agent to call next based on analysis so far
    3. Interpret results from each agent call and build cumulative understanding
    4. Make a final determination on root cause when confident
    
    Process:
    - Always begin with examining lab environment (most common issues)
    - If lab analysis is inconclusive, examine infrastructure next
    - Only if both above are inconclusive, examine script issues
    - Maintain a cumulative knowledge base about the failure as you proceed
    
    Your final output should be a complete analysis with:
    - Determined root cause category
    - Confidence level (0-100)
    - Evidence supporting the conclusion
    - Reasoning process
    - Specific recommendations for fixing the issue
    """

# Shared context updating function
@function_tool
def update_analysis_context(
        new_findings: Dict[str, Any],
        new_evidence: List[str]
) -> Dict[str, Any]:
    """Update the shared analysis context with new findings and evidence"""
    # This would be implemented to update the context
    # For the example, we'll return a placeholder
    return {
        "status": "updated",
        "new_evidence_count": len(new_evidence)
    }



# Add a context management function to process and maintain context between calls
# @function_tool
# def update_analysis_context(
#         agent_name: str,
#         findings: Dict[str, Any],
#         evidence: List[str],
#         additional_query: Optional[str] = None
# ) -> Dict[str, Any]:
#     """Update the analysis context with findings from an agent call.
#
#     Args:
#         agent_name: Name of the agent that produced these findings
#         findings: Dictionary of findings from the agent
#         evidence: List of evidence strings
#         additional_query: Optional follow-up query for the next call
#
#     Returns:
#         Updated context dictionary
#     """
#     # This would update the global context object in a real implementation
#     return {
#         "status": "updated",
#         "agent_name": agent_name,
#         "evidence_count": len(evidence),
#         "query_for_next_call": additional_query
#     }



# Log retrieval tool available to all agents
@function_tool
def get_additional_logs(
        pattern: str,
        context_lines: int = 10
) -> str:
    """Retrieve additional log content based on a search pattern"""
    # Implementation would search for the pattern and return context
    # For the example, we'll return a placeholder
    return f"Additional logs for pattern: {pattern}\n[Sample log content with {context_lines} lines of context]"

class CIAnalysisSolution:
    def __init__(self):
        # Create the specialized agents
        self.lab_agent = Agent(
            name="lab_agent",
            instructions=lab_agent_instructions(),
            tools=[get_additional_logs],
        )

        self.infra_agent = Agent(
            name="infra_agent",
            instructions=infra_agent_instructions(),
            tools=[get_additional_logs],
        )

        self.script_agent = Agent(
            name="script_agent",
            instructions=script_agent_instructions(),
            tools=[get_additional_logs],
        )

        # Create the orchestrator with all specialized agents as tools
        self.orchestrator_agent = Agent(
            name="orchestrator_agent",
            instructions=orchestrator_instructions(),
            tools=[
                self.lab_agent.as_tool(
                    tool_name="analyze_lab_environment",
                    tool_description="Analyze if failure is caused by a lab environment issue"
                ),
                self.infra_agent.as_tool(
                    tool_name="analyze_infrastructure",
                    tool_description="Analyze if failure is caused by an infrastructure issue"
                ),
                self.script_agent.as_tool(
                    tool_name="analyze_scripts",
                    tool_description="Analyze if failure is caused by an automation script issue"
                ),
                update_analysis_context,
                get_additional_logs
            ]
        )

        # Create a synthesizer agent for final analysis
        self.synthesizer_agent = Agent(
            name="synthesizer_agent",
            instructions="Review all analysis performed by specialized agents and produce a final, coherent assessment with clear root cause and resolution steps.",
        )

    async def analyze_failure(self, test_id: str, initial_logs: str) -> AnalysisResult:
        # Initialize analysis context
        context = AnalysisContext(
            test_id=test_id,
            logs=initial_logs
        )

        # Use a trace to keep all analysis in one context
        with trace(f"Failure analysis for {test_id}"):
            # Run the orchestrator with full context
            orchestrator_result = await Runner.run(self.orchestrator_agent, context)

            # Extract rich analysis data from the orchestrator run
            analysis_data = self._process_orchestrator_result(orchestrator_result)

            # Run the synthesizer to produce final coherent output
            synthesizer_result = await Runner.run(
                self.synthesizer_agent,
                {
                    "original_context": context,
                    "analysis_results": analysis_data
                }
            )

            # Return the final analyzed result
            return self._create_final_result(synthesizer_result)

    def _process_orchestrator_result(self, result):
        """Extract all analysis data from orchestrator's tool calls"""
        analysis_data = {
            "lab_analysis": None,
            "infra_analysis": None,
            "script_analysis": None,
            "tool_calls": []
        }

        # Process all tool calls and extract the results
        for item in result.new_items:
            if isinstance(item, ToolCallItem):
                tool_data = {
                    "tool": item.tool_name,
                    "input": item.input,
                    "output": item.output
                }
                analysis_data["tool_calls"].append(tool_data)

                # Store specialized analysis results
                if item.tool_name == "analyze_lab_environment":
                    analysis_data["lab_analysis"] = item.output
                elif item.tool_name == "analyze_infrastructure":
                    analysis_data["infra_analysis"] = item.output
                elif item.tool_name == "analyze_scripts":
                    analysis_data["script_analysis"] = item.output

        return analysis_data

    def _create_final_result(self, synthesizer_result) -> AnalysisResult:
        """Convert synthesizer output to AnalysisResult"""
        # Extract final analysis from synthesizer's output
        final_output = synthesizer_result.final_output

        # In a real implementation, you'd parse the output into structured form
        # For example purposes, we're creating a sample result
        return AnalysisResult(
            root_cause=final_output.get("root_cause", "Unknown"),
            confidence=final_output.get("confidence", 0),
            evidence=final_output.get("evidence", []),
            reasoning=final_output.get("reasoning", ""),
            recommendations=final_output.get("recommendations", [])
        )

# Usage example
async def main():
    analyzer = CIAnalysisSolution()
    test_id = "test-123456"
    initial_logs = "Sample initial logs for the test run..."

    result = await analyzer.analyze_failure(test_id, initial_logs)
    print(f"Root cause: {result.root_cause} (Confidence: {result.confidence}%)")
    print(f"Evidence: {', '.join(result.evidence[:3])}...")
    print(f"Recommendations: {', '.join(result.recommendations[:2])}...")

if __name__ == "__main__":
    asyncio.run(main())