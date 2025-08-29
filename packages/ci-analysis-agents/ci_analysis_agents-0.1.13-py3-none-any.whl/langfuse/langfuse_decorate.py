import asyncio
import functools
from typing import Callable, Any, Coroutine, TypeVar, cast
from langfuse.langfuse_config import load_config, get_user_id, get_trace_url

T = TypeVar('T')


def langfuse_task(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        load_config()
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        trace_provider = TracerProvider()
        trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

        from opentelemetry import trace
        trace.set_tracer_provider(trace_provider)

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("OpenAI-Agent-Trace") as span:
            user_id = get_user_id()
            span.set_attribute("langfuse.user.id", user_id)
            url = get_trace_url(user_id)
            print(f"Langfuse url:{url}")
            loop = asyncio.get_running_loop()
            task = loop.create_task(func(*args, **kwargs))
            result = await task
        return cast(T, result)

    return wrapper
