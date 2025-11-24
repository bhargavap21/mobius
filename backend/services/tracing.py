"""
Tracing Service - Arize Phoenix integration for LLM observability

Provides comprehensive tracing for all LLM calls, strategy generation,
and backtest execution to enable debugging and evaluation.
"""

import logging
import os
from typing import Optional, Any, Dict
from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger(__name__)

# Global state for tracing
_tracer_provider = None
_anthropic_instrumentor = None
_is_initialized = False


def init_tracing(
    project_name: str = "mobius-trading-bot",
    phoenix_endpoint: Optional[str] = None,
    enable_phoenix_server: bool = True
) -> bool:
    """
    Initialize Phoenix tracing for the application.

    Args:
        project_name: Name of the project in Phoenix UI
        phoenix_endpoint: Optional custom Phoenix collector endpoint
        enable_phoenix_server: Whether to start local Phoenix server (for dev)

    Returns:
        True if initialization successful, False otherwise
    """
    global _tracer_provider, _anthropic_instrumentor, _is_initialized

    if _is_initialized:
        logger.info("Tracing already initialized")
        return True

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from openinference.instrumentation.anthropic import AnthropicInstrumentor

        # Determine Phoenix endpoint
        if phoenix_endpoint:
            endpoint = phoenix_endpoint
        elif os.getenv("PHOENIX_COLLECTOR_ENDPOINT"):
            endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT")
        else:
            # Default to local Phoenix server
            endpoint = "http://localhost:6006/v1/traces"

        # Start local Phoenix server in development
        if enable_phoenix_server and "localhost" in endpoint:
            try:
                import phoenix as px
                # Launch Phoenix in background (non-blocking)
                px.launch_app()
                logger.info("🔥 Phoenix server started at http://localhost:6006")
            except Exception as e:
                logger.warning(f"Could not start Phoenix server: {e}")
                logger.info("Phoenix may already be running or endpoint is remote")

        # Create resource with project metadata
        resource = Resource.create({
            "service.name": project_name,
            "service.version": "1.0.0",
            "deployment.environment": os.getenv("ENVIRONMENT", "development")
        })

        # Set up tracer provider
        _tracer_provider = TracerProvider(resource=resource)

        # Configure OTLP exporter to Phoenix
        otlp_exporter = OTLPSpanExporter(endpoint=endpoint)
        span_processor = BatchSpanProcessor(otlp_exporter)
        _tracer_provider.add_span_processor(span_processor)

        # Set as global tracer provider
        trace.set_tracer_provider(_tracer_provider)

        # Instrument Anthropic client
        _anthropic_instrumentor = AnthropicInstrumentor()
        _anthropic_instrumentor.instrument()

        _is_initialized = True
        logger.info(f"✅ Tracing initialized - sending to {endpoint}")
        logger.info(f"   Project: {project_name}")
        logger.info(f"   View traces at: http://localhost:6006")

        return True

    except ImportError as e:
        logger.error(f"❌ Missing tracing dependencies: {e}")
        logger.error("   Run: pip install arize-phoenix openinference-instrumentation-anthropic")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to initialize tracing: {e}")
        return False


def shutdown_tracing():
    """Gracefully shutdown tracing and flush any pending spans."""
    global _tracer_provider, _anthropic_instrumentor, _is_initialized

    if not _is_initialized:
        return

    try:
        if _anthropic_instrumentor:
            _anthropic_instrumentor.uninstrument()

        if _tracer_provider:
            _tracer_provider.shutdown()

        _is_initialized = False
        logger.info("Tracing shutdown complete")

    except Exception as e:
        logger.error(f"Error during tracing shutdown: {e}")


def get_tracer(name: str = "mobius"):
    """Get a tracer instance for creating custom spans."""
    from opentelemetry import trace
    return trace.get_tracer(name)


@contextmanager
def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracing custom operations.

    Usage:
        with trace_operation("parse_strategy", {"user_input": description}):
            result = parse_strategy(description)
    """
    if not _is_initialized:
        yield
        return

    tracer = get_tracer()
    with tracer.start_as_current_span(operation_name) as span:
        if attributes:
            for key, value in attributes.items():
                # Convert complex types to strings
                if isinstance(value, (dict, list)):
                    import json
                    span.set_attribute(key, json.dumps(value)[:1000])  # Limit size
                elif value is not None:
                    span.set_attribute(key, str(value)[:1000])

        try:
            yield span
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            raise


def trace_function(operation_name: Optional[str] = None):
    """
    Decorator for tracing function calls.

    Usage:
        @trace_function("strategy_generation")
        def generate_strategy(description: str) -> dict:
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__

            if not _is_initialized:
                return func(*args, **kwargs)

            tracer = get_tracer()
            with tracer.start_as_current_span(name) as span:
                # Add function arguments as attributes (safely)
                try:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    # Log first few args (be careful with sensitive data)
                    if args:
                        span.set_attribute("args.count", len(args))
                    if kwargs:
                        span.set_attribute("kwargs.keys", str(list(kwargs.keys())))
                except Exception:
                    pass

                try:
                    result = func(*args, **kwargs)

                    # Mark success
                    span.set_attribute("success", True)

                    # Log result type
                    if result is not None:
                        span.set_attribute("result.type", type(result).__name__)

                    return result

                except Exception as e:
                    span.set_attribute("error", True)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise

        return wrapper
    return decorator


def add_span_attributes(attributes: Dict[str, Any]):
    """Add attributes to the current active span."""
    if not _is_initialized:
        return

    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        if span:
            for key, value in attributes.items():
                if isinstance(value, (dict, list)):
                    import json
                    span.set_attribute(key, json.dumps(value)[:1000])
                elif value is not None:
                    span.set_attribute(key, str(value)[:1000])
    except Exception as e:
        logger.debug(f"Could not add span attributes: {e}")


def log_strategy_generation(
    user_input: str,
    parsed_strategy: Dict[str, Any],
    validation_passed: bool,
    generation_time_ms: float
):
    """Log strategy generation event with structured data."""
    add_span_attributes({
        "strategy.user_input": user_input[:500],
        "strategy.name": parsed_strategy.get("name", "unknown"),
        "strategy.asset": parsed_strategy.get("asset", "unknown"),
        "strategy.signal_type": parsed_strategy.get("entry_conditions", {}).get("signal", "unknown"),
        "strategy.validation_passed": validation_passed,
        "strategy.generation_time_ms": generation_time_ms,
        "strategy.has_partial_exit": parsed_strategy.get("exit_conditions", {}).get("take_profit_pct_shares", 1.0) < 1.0,
        "strategy.has_trailing_stop": parsed_strategy.get("exit_conditions", {}).get("stop_loss") is not None,
    })


def log_backtest_result(
    strategy_name: str,
    total_return: float,
    total_trades: int,
    win_rate: float,
    execution_time_ms: float
):
    """Log backtest execution result."""
    add_span_attributes({
        "backtest.strategy_name": strategy_name,
        "backtest.total_return_pct": total_return,
        "backtest.total_trades": total_trades,
        "backtest.win_rate_pct": win_rate,
        "backtest.execution_time_ms": execution_time_ms,
    })


def log_evaluation_result(
    evaluator_name: str,
    passed: bool,
    score: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log evaluation result from deterministic or LLM-as-judge evaluator."""
    attrs = {
        f"eval.{evaluator_name}.passed": passed,
    }
    if score is not None:
        attrs[f"eval.{evaluator_name}.score"] = score
    if details:
        import json
        attrs[f"eval.{evaluator_name}.details"] = json.dumps(details)[:500]

    add_span_attributes(attrs)


# Auto-initialize on import if PHOENIX_AUTO_INIT is set
if os.getenv("PHOENIX_AUTO_INIT", "").lower() == "true":
    init_tracing()
