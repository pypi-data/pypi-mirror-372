from enum import Enum
from pydantic import BaseModel
from typing import Any, Union, Type, Dict


class FailureType(str, Enum):
    LAB_ISSUE = "Lab_Issue"
    INFRA_ISSUE = "Infrastructure_Issue"
    AT_SCRIPT = "AT_Script"
    UNKNOWN = "Unknown"


class AIActionInsight(BaseModel):
    pass


class ENVIssueActionInsight(AIActionInsight):
    api_url: str
    http_status_code: int
    request_id: str
    detail_log: str


class InfraIssueActionInsight(AIActionInsight):
    device_udid: str
    device_host: str
    detail_log: str
    error_type: str


class ATScriptActionInsight(AIActionInsight):
    code_line: str


class AIResponse(BaseModel):
    root_cause_insight: str
    action_insight: AIActionInsight


class ENVIssueAIResponse(AIResponse):
    failed_by_env: bool
    action_insight: ENVIssueActionInsight


class InfraIssueAIResponse(AIResponse):
    failed_by_infra: bool
    action_insight: InfraIssueActionInsight


class ATScriptAIResponse(AIResponse):
    failed_by_at_script: bool
    action_insight: ATScriptActionInsight


class AnalysisContext(BaseModel):
    test_id: str = ""
    backend_api_log: str = ""
    app_log: str = ""
    appium_log: str = ""
    device_log: str = ""
    failure_log: str = ""
    failed_thread_log: str = ""
    env_issue_response: ENVIssueAIResponse = None
    infra_issue_response: InfraIssueAIResponse = None
    at_script_issue_response: ATScriptAIResponse = None
    generic_response: AIResponse = None
    beats_metadata: Any = None
    device_record_metadata: Any = None


class LastAnalysisResult(BaseModel):
    failure_type: FailureType
    evidence: str
    confidence_score: float


class AnalysisResult(BaseModel):
    last_agent_report: LastAnalysisResult
    response_detail: Union[ENVIssueAIResponse, InfraIssueAIResponse, ATScriptAIResponse, AIResponse]


# ============================================================================
# FAILURE TYPE MAPPING CONFIGURATION
# ============================================================================
# This mapping connects 'FailureType' enum values to their corresponding 'response types' and 'context attributes'.

class FailureTypeMappingConfig:
    """Configuration class that defines the mapping between FailureType and response types"""

    def __init__(self):
        self._mappings = {
            FailureType.LAB_ISSUE: {
                'response_type': ENVIssueAIResponse,
                'context_attr': 'env_issue_response',
                'flag_attr': 'failed_by_env',
                'log_message': 'Lab Issue'
            },
            FailureType.INFRA_ISSUE: {
                'response_type': InfraIssueAIResponse,
                'context_attr': 'infra_issue_response',
                'flag_attr': 'failed_by_infra',
                'log_message': 'Infrastructure Issue'
            },
            FailureType.AT_SCRIPT: {
                'response_type': ATScriptAIResponse,
                'context_attr': 'at_script_issue_response',
                'flag_attr': 'failed_by_at_script',
                'log_message': 'AT Script Issue'
            },
            FailureType.UNKNOWN: {
                'response_type': AIResponse,
                'context_attr': 'generic_response',
                'flag_attr': None,  # No flag for unknown type
                'log_message': 'Unknown Issue'
            }
        }

    def get_mapping(self, failure_type: FailureType) -> Dict[str, Any]:
        """Get mapping configuration for a failure type"""
        if failure_type not in self._mappings:
            raise ValueError(f"FailureType {failure_type} is not mapped in FailureTypeMappingConfig,please configure this type into the {AnalysisContext.__name__} and _mappings.")
        return self._mappings[failure_type]

    def get_response_type(self, failure_type: FailureType) -> Type[AIResponse]:
        return self.get_mapping(failure_type)['response_type']

    def get_context_attr(self, failure_type: FailureType) -> str:
        return self.get_mapping(failure_type)['context_attr']

    def get_flag_attr(self, failure_type: FailureType) -> str | None:
        """Get the flag attribute name for a failure type. Returns None for UNKNOWN type."""
        flag_attr = self.get_mapping(failure_type)['flag_attr']
        return flag_attr

    def get_log_message(self, failure_type: FailureType) -> str:
        """Get the log message for a failure type"""
        return self.get_mapping(failure_type)['log_message']

    def get_response_to_context_mappings(self) -> Dict[Type[AIResponse], str]:
        """Get mappings for save_response_to_context function"""
        mappings = {}
        for failure_type, config in self._mappings.items():
            mappings[config['response_type']] = config['context_attr']
        return mappings

    def get_all_failure_types(self) -> list[FailureType]:
        """Get all supported failure types"""
        return list(self._mappings.keys())

    def parse_response_detail(self, failure_type: FailureType, ai_result_json: dict) -> AIResponse:
        response_type = self.get_response_type(failure_type)
        return response_type.model_validate(ai_result_json)


FAILURE_TYPE_MAPPING = FailureTypeMappingConfig()
