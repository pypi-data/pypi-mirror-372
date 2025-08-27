# -*- coding: utf-8 -*-
"""
The `tracing` module provides a centralized and configurable implementation for distributed tracing using OpenTelemetry. It is designed to monitor the execution flow of the Reasoning Kernel, offering insights into performance and helping to diagnose issues. The module supports multiple exporters, including OTLP for production environments and a console exporter for local development. It also includes a `trace_operation` decorator that makes it easy to instrument specific functions and methods, allowing developers to trace operations with minimal code changes. Furthermore, it integrates with the logging system to correlate traces with logs, providing a comprehensive view of the application's behavior.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

# Optional OpenTelemetry imports - gracefully handle missing dependencies
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.info(
        'OpenTelemetry not available. Install with: uv pip install -e ".[observability]"'
    )

logger = logging.getLogger(__name__)


def initialize_tracing(
    service_name: str = "reasoning-kernel",
    otlp_endpoint: Optional[str] = None,
) -> None:
    """
    Initialize OpenTelemetry tracing.

    Args:
        service_name: The name of the service.
        otlp_endpoint: The OTLP endpoint for exporting traces.
    """
    if not OPENTELEMETRY_AVAILABLE:
        logger.info("OpenTelemetry not available. Tracing disabled.")
        return

    resource = Resource(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # Add console exporter
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    # Add OTLP exporter if an endpoint is provided
    if otlp_endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
        )

    # Instrument logging
    LoggingInstrumentor().instrument(set_logging_format=True)

    logger.info("OpenTelemetry tracing initialized.")


def trace_operation(name: str) -> Callable:
    """
    A decorator to trace the execution of a function.

    Args:
        name: The name of the span.

    Returns:
        The decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not OPENTELEMETRY_AVAILABLE:
                # Just execute the function without tracing
                return await func(*args, **kwargs)

            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(name) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.record_exception(e)
                    raise

        return wrapper

    return decorator
