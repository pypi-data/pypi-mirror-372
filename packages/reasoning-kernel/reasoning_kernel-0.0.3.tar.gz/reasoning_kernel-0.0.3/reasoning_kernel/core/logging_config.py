"""Central structured logging configuration utilities."""

from contextlib import contextmanager
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional
import uuid

import structlog



DEFAULT_FORMAT = "[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s"

# Global request context storage
_request_context: Dict[str, Any] = {}


def get_request_id() -> str:
    """Get current request ID from context, or generate a new one."""
    return _request_context.get("request_id", str(uuid.uuid4()))


def get_request_context() -> Dict[str, Any]:
    """Get current request context."""
    return _request_context.copy()


@contextmanager
def request_context(request_id: str, **context):
    """Context manager for setting request-specific logging context."""
    global _request_context
    old_context = _request_context.copy()
    _request_context.update({"request_id": request_id, **context})
    try:
        yield
    finally:
        _request_context = old_context


def add_request_context(logger, method_name, event_dict):
    """Add request context to log events."""
    event_dict.update(_request_context)
    return event_dict


def add_service_context(logger, method_name, event_dict):
    """Add service-level context to log events."""
    event_dict.update({
        "service": "reasoning-kernel",
        "version": "0.0.2",
        "environment": os.getenv("ENVIRONMENT", "development")
    })
    return event_dict


def configure_logging(level: str = "INFO", json_logs: bool = False, enable_colors: bool = True):
    """Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_logs: Whether to output logs in JSON format
        enable_colors: Whether to enable colored output (for CLI)
    """
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        add_request_context,
        add_service_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_logs:
        # JSON output for production
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ])
    else:
        # Human-readable output for CLI/development
        processors.extend([
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(colors=enable_colors) if enable_colors 
            else structlog.processors.JSONRenderer()
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format=DEFAULT_FORMAT,
        level=log_level,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return structlog.get_logger()








def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Structured logger instance
    """
    # Ensure structlog is configured if not already
    if not logging.getLogger().handlers:
        configure_logging(level="INFO", json_logs=False, enable_colors=True)
    
    try:
        # Try to get a structlog logger
        return structlog.get_logger(name)
    except Exception:
        # If structlog still fails, create a basic configured logger
        configure_logging(level="INFO", json_logs=False, enable_colors=True)
        return structlog.get_logger(name)


def safe_log(logger, level: str, message: str, **kwargs):
    """Safely log a message with fallback to basic logging if structured logging fails."""
    try:
        if level == "info":
            logger.info(message, **kwargs)
        elif level == "error":
            logger.error(message, **kwargs)
        elif level == "warning":
            logger.warning(message, **kwargs)
        elif level == "debug":
            logger.debug(message, **kwargs)
        else:
            logger.info(message, **kwargs)
    except Exception:
        # Fallback to basic logging
        fallback_message = f"{message}"
        if kwargs:
            fallback_message += f" - {kwargs}"
        if level == "info":
            logger.info(fallback_message)
        elif level == "error":
            logger.error(fallback_message)
        elif level == "warning":
            logger.warning(fallback_message)
        elif level == "debug":
            logger.debug(fallback_message)
        else:
            logger.info(fallback_message)


@contextmanager
def performance_context(operation: str, logger: Optional[structlog.stdlib.BoundLogger] = None):
    """Context manager for performance logging with duration tracking."""
    if logger is None:
        logger = get_logger("performance")

    start_time = time.time()
    safe_log(logger, "info", "Operation started", operation=operation, start_time=start_time)

    try:
        yield logger
        duration = time.time() - start_time
        safe_log(logger, "info", "Operation completed", operation=operation, duration=duration, status="success")
    except Exception as e:
        duration = time.time() - start_time
        safe_log(
            logger, "error", "Operation failed", operation=operation, duration=duration, status="error", error=str(e)
        )
        raise


@contextmanager
def error_context(logger: structlog.stdlib.BoundLogger, operation: str, **context):
    """Enhanced error context manager for detailed error logging."""
    import traceback

    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    try:
        yield logger
    except Exception as e:
        # Capture detailed error information
        error_info = {
            "operation": operation,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "correlation_id": get_correlation_id(),
            "traceback": traceback.format_exc(),
            **context,
        }

        # Add system context
        import sys

        error_info.update(
            {
                "python_version": sys.version,
                "request_context": get_request_context(),
            }
        )

        # Log with enhanced context
        logger.error("Error in error_context", **error_info)
        raise


def log_stage_error(
    logger: structlog.stdlib.BoundLogger,
    stage_name: str,
    error: Exception,
    context: Dict[str, Any],
    **additional_context,
) -> Dict[str, Any]:
    """Enhanced error logging for MSA pipeline stages."""
    import traceback

    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    error_details = {
        "stage": stage_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "correlation_id": get_correlation_id(),
        "session_id": context.get("session_id"),
        "scenario_preview": context.get("scenario", "")[:100] if context.get("scenario") else "",
        "stage_context": context,
        "traceback": traceback.format_exc(),
        **additional_context,
    }

    logger.error("Stage error occurred", **error_details)
    return error_details


def create_error_breadcrumbs() -> List[Dict[str, Any]]:
    """Create error breadcrumbs for debugging context."""
    import inspect

    breadcrumbs = []

    # Get current stack frames
    current_frame = inspect.currentframe()
    try:
        frames = inspect.getouterframes(current_frame)
        for frame_info in frames[:10]:  # Limit to 10 frames
            breadcrumb = {
                "filename": frame_info.filename.split("/")[-1],  # Just filename
                "function": frame_info.function,
                "line_number": frame_info.lineno,
                "code_context": frame_info.code_context[0].strip() if frame_info.code_context else None,
            }
            breadcrumbs.append(breadcrumb)
    finally:
        del current_frame  # Prevent reference cycles

    return breadcrumbs


def log_with_breadcrumbs(logger: structlog.stdlib.BoundLogger, level: str, message: str, **kwargs):
    """Log with error breadcrumbs for enhanced debugging context."""
    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    enhanced_context = {"correlation_id": get_correlation_id(), "breadcrumbs": create_error_breadcrumbs(), **kwargs}

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, **enhanced_context)


class MSAStageLogger:
    """Specialized logger for MSA pipeline stages with enhanced context."""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.logger = get_logger(f"msa.stage.{stage_name}")
        self._stage_context: Dict[str, Any] = {}

    def set_stage_context(self, **context):
        """Set stage-specific context."""
        self._stage_context.update(context)

    def log_stage_start(self, **context):
        """Log stage start with context."""
        log_context = {
            "stage": self.stage_name,
            "correlation_id": None,  # Simplified - no tracing
            "stage_event": "stage_start",
            **self._stage_context,
            **context,
        }
        self.logger.info("MSA stage started", **log_context)

    def log_stage_complete(self, duration: float, **context):
        """Log stage completion with performance metrics."""
        log_context = {
            "stage": self.stage_name,
            "correlation_id": None,  # Simplified - no tracing
            "stage_event": "stage_complete",
            "duration": duration,
            **self._stage_context,
            **context,
        }
        self.logger.info("MSA stage completed", **log_context)

    def log_stage_error(self, error: Exception, **context):
        """Log stage error with enhanced context."""
        return log_stage_error(self.logger, self.stage_name, error, {**self._stage_context, **context})

    def debug(self, message: str, **kwargs):
        """Debug logging with stage context."""
        self.logger.debug(message, stage=self.stage_name, **self._stage_context, **kwargs)

    def info(self, message: str, **kwargs):
        """Info logging with stage context."""
        self.logger.info(message, stage=self.stage_name, **self._stage_context, **kwargs)

    def warning(self, message: str, **kwargs):
        """Warning logging with stage context."""
        self.logger.warning(message, stage=self.stage_name, **self._stage_context, **kwargs)

    def error(self, message: str, **kwargs):
        """Error logging with stage context."""
        self.logger.error(
            message,
            stage=self.stage_name,
            **self._stage_context,
            **kwargs,
        )
