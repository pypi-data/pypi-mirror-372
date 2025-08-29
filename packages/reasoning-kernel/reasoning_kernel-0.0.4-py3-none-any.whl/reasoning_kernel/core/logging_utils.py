"""Utility functions for logging to avoid circular imports."""

from typing import Dict, Any


def _is_structlog_logger(logger: object) -> bool:
    """Best-effort check whether this logger is a structlog logger."""
    try:
        import structlog  # type: ignore

        return isinstance(logger, (structlog.stdlib.BoundLogger, structlog.BoundLogger))  # type: ignore[attr-defined]
    except Exception:
        return False


def simple_log_error(logger, operation_name: str, error: Exception, **kwargs):
    """
    Log an error in a way that works for both structlog and stdlib logging.

    Args:
        logger: Logger instance (supports both logging.Logger and structlog)
        operation_name: Name of the operation that failed
        error: Exception that occurred
        **kwargs: Additional context to include in the log
    """
    error_info: Dict[str, Any] = {
        "operation": operation_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        **kwargs,
    }

    if _is_structlog_logger(logger):
        # structlog supports keyword kvs directly
        logger.error("Operation failed", **error_info)
        return

    # stdlib logging does not accept arbitrary kwargs; use extra=
    # Move fields under a single key to avoid polluting the record namespace
    msg = f"Operation failed: {operation_name}"
    logger.error(msg, extra={"error": error_info})
