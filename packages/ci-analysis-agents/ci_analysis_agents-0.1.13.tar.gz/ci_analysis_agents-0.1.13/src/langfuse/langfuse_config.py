import os
import base64

import nest_asyncio
import logfire
from agents import set_tracing_disabled

def load_config():
    # #disable tracing for the OpenAI Agents SDK
    # set_tracing_disabled(True)

    os.environ["LANGFUSE_PUBLIC_KEY"] = "sk-lf-d44e8602-ac86-4c42-ab42-f5ba42b5214d"
    os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-d44e8602-ac86-4c42-ab42-f5ba42b5214d"
    os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com"

    LANGFUSE_AUTH = base64.b64encode(
        f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
    ).decode()

    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

    nest_asyncio.apply()

    logfire.configure(
        service_name='ci_agent',
        send_to_logfire=False,
        scrubbing=False
    )
    # This method automatically patches the OpenAI Agents SDK to send logs via OTLP to Langfuse.
    logfire.instrument_openai_agents()


def get_trace_url(user_id: str) -> str:
    host = os.environ.get("LANGFUSE_HOST")
    return f"{host}/project/cmaoxupai007gad07qlvsutd6/users/{user_id}"


def get_user_id() -> str:
    return os.environ.get("LANGFUSE_USER_ID", "rc")
