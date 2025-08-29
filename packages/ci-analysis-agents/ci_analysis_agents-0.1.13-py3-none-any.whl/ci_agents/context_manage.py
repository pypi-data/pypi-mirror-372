from typing import Any
from .log_config import logger
from .types import AIResponse, AnalysisContext, LastAnalysisResult, AnalysisResult, FAILURE_TYPE_MAPPING


def save_response_to_context(context: AnalysisContext, output: Any) -> None:
    """Save agent response to the appropriate context field using centralized mapping"""
    response_mappings = FAILURE_TYPE_MAPPING.get_response_to_context_mappings()
    output_type = type(output)
    if output_type in response_mappings:
        context_attr = response_mappings[output_type]
        logger.debug(f"save_response_to_context: {output_type.__name__} -> {context_attr}")
        setattr(context, context_attr, output)
        return
    if AIResponse in output_type.__mro__:
        logger.info(f"Unknown AIResponse subclass {output_type.__name__}, saving to generic_response")
        context.generic_response = output
    else:
        logger.debug(f"Output is not an AIResponse type: {output_type.__name__}")


def conclude_ai_response(last_agent_result: LastAnalysisResult, context: AnalysisContext) -> AnalysisResult:
    """Create AnalysisResult using centralized failure type mapping"""
    logger.info(f"Concluding AI response for failure type: {last_agent_result.failure_type}")
    try:
        mapping = FAILURE_TYPE_MAPPING.get_mapping(last_agent_result.failure_type)
        context_attr = mapping['context_attr']
        flag_attr = mapping['flag_attr']  # This can be None for UNKNOWN type
        log_message = mapping['log_message']
        context_response = getattr(context, context_attr)

        if context_response and flag_attr is not None:
            # For types with flag attributes, check the flag value
            flag_value = getattr(context_response, flag_attr)
            logger.info(f"Hub Agent concluded as {log_message} and The {log_message} agent result with: {flag_value}.")
        elif context_response:
            # For types without flag attributes (like UNKNOWN) or when flag_attr is None
            logger.info(f"Hub Agent concluded as {log_message} with response available.")
        else:
            # No agent response found - create fallback
            logger.info(f"Hub Agent concluded as {log_message} but no agent response found.")
            if context.generic_response:
                logger.info("Using generic_response as fallback for response_detail")
                context_response = context.generic_response
            else:
                # Create a minimal fallback AIResponse based on hub agent's analysis
                from .types import AIResponse, AIActionInsight
                logger.info("Creating fallback AIResponse from hub agent analysis")
                context_response = AIResponse(
                    root_cause_insight=last_agent_result.evidence,
                    action_insight=AIActionInsight()
                )

        analysis_result = AnalysisResult(last_agent_report=last_agent_result, response_detail=context_response)
        return analysis_result

    except ValueError as e:
        # This will catch unmapped failure types
        logger.error(f"Failed to process failure type {last_agent_result.failure_type}: {e}")
        raise e
