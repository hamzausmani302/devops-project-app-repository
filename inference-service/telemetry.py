
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextlib import contextmanager


from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode





from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor
)
from opentelemetry.context import Context

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
    
)
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter



def configure_opentelemetry(config):

    resource = Resource.create({
        "service.name": config.app_name,
        "service.version": config.version,
    })

    provider = TracerProvider(
        resource=resource
    )

    exporter = OTLPSpanExporter(
        endpoint="localhost:4317",
        insecure=True,
    )
    # exporter = ConsoleSpanExporter()
    provider.add_span_processor(
        BatchSpanProcessor(exporter)                                                    
    )

    trace.set_tracer_provider(provider)

    return provider

##### DECORATOR for telemtry tracing

import functools
import inspect

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer("app.instrumentation")



def trace_function(
    name: str = None,
    attributes: dict = None,
):
    """
    OpenTelemetry decorator supporting sync and async functions.
    """

    def decorator(func):

        span_name = name or func.__qualname__

        def set_attributes(span, args, kwargs):
            if attributes:
                for key, value in attributes.items():
                    if value is not None:
                        span.set_attribute(key, value)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                with tracer.start_as_current_span(
                    span_name
                ) as span:

                    set_attributes(span, args, kwargs)

                    try:
                        return await func(*args, **kwargs)

                    except Exception as exc:
                        span.record_exception(exc)
                        span.set_status(
                            Status(StatusCode.ERROR)
                        )
                        raise

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):

            with tracer.start_as_current_span(
                span_name
            ) as span:

                set_attributes(span, args, kwargs)

                try:
                    return func(*args, **kwargs)

                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(
                        Status(StatusCode.ERROR)
                    )
                    raise

        return sync_wrapper

    return decorator




@contextmanager
def trace_span(
    name: str,
    attributes: dict | None = None,
    span_kind: SpanKind = SpanKind.INTERNAL,
    parent_context: Context | None = None,
):
    with tracer.start_as_current_span(
        name,
        attributes=attributes or {},
        kind=span_kind,
        context=parent_context,
    ) as span:
        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR))
            raise