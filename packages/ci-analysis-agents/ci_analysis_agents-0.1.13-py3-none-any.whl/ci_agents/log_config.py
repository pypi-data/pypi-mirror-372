import logging
import logging.config
import sys


class TracingErrorFilter(logging.Filter):
    """Filter out OpenAI tracing 40X errors while keeping other logs"""

    def filter(self, record):
        # Block messages about tracing client 40X errors
        message = record.getMessage()
        if 'Tracing client error 40' in message or 'api.openai.com/v1/traces/ingest' in message:
            return False
        return True


class RobustStreamHandler(logging.StreamHandler):
    """Custom handler that gracefully handles closed streams"""

    def emit(self, record):
        try:
            if hasattr(self.stream, 'closed') and self.stream.closed:
                return  # Silently skip if stream is closed
            super().emit(record)
        except (ValueError, OSError):
            pass

    def flush(self):
        try:
            if hasattr(self.stream, 'closed') and not self.stream.closed:
                super().flush()
        except (ValueError, OSError):
            pass


class SmartFormatter(logging.Formatter):
    """Custom formatter that applies different formats based on logger name"""

    def __init__(self):
        # Define formats for different loggers
        self.formatters = {
            'detailed': logging.Formatter('[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)d]%(message)s'),
            'simple': logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]%(message)s'),
        }

    def format(self, record):
        # Use detailed format for ci_agents and tests, simple for others
        if record.name.startswith('ci_agents'):
            return self.formatters['detailed'].format(record)
        else:
            return self.formatters['simple'].format(record)


# Logging configuration for the SDK
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'smart': {
            '()': SmartFormatter,
        }
    },
    'filters': {
        'tracing_error': {
            '()': TracingErrorFilter,
        }
    },
    'handlers': {
        'console_unified': {
            'level': 'DEBUG',
            '()': RobustStreamHandler,
            'formatter': 'smart',
            'stream': sys.stdout
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console_unified']
    },
    'loggers': {
        # Unified CI Agents SDK - use detailed format
        'ci_agents': {
            'handlers': ['console_unified'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # OpenAI agents logger - use simple format  
        'openai.agents': {
            'handlers': ['console_unified'],
            'level': 'DEBUG',
            'propagate': False,
            'filters': ['tracing_error'],
        },
    },
}

# Global logger for the entire SDK - import this instead of creating new loggers
logger = logging.getLogger("ci_agents")


def configure_root_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    logger.info("Logging configured for SDK")
    problematic_loggers = ["httpx", "urllib3", "agents", "agents.tracing", "opentelemetry"]
    robust_handler = RobustStreamHandler(sys.stdout)
    robust_handler.setLevel(logging.INFO)
    for logger_name in problematic_loggers:
        bg_logger = logging.getLogger(logger_name)
        bg_logger.handlers.clear()
        bg_logger.addHandler(robust_handler)
        bg_logger.propagate = False


async def wait_for_background_logging(timeout: float = 2.0):
    """Wait for background logging threads to complete before shutdown"""
    import asyncio
    import threading

    def wait_and_flush():
        for handler in logging.getLogger().handlers:
            try:
                handler.flush()
            except (ValueError, OSError):
                pass

        # Wait for background threads with logging-related names
        for thread in threading.enumerate():
            if thread != threading.current_thread() and thread.is_alive():
                thread_name = getattr(thread, 'name', '').lower()
                if any(name in thread_name for name in ['trace', 'export', 'telemetry', 'agent', 'batch', 'processor']):
                    try:
                        thread.join(timeout=0.5)  # Slightly longer per thread
                    except Exception:
                        pass

    try:
        await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, wait_and_flush),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        pass  # Continue if timeout - don't block main process
