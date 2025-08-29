"""
Lightweight Performance Profiling
=================================

Provides a simple performance monitor for tracking execution time and memory usage.
This module is a replacement for the previously missing profiling functionality.
"""

import time
import memory_profiler
from contextlib import contextmanager
from functools import wraps
import logging

logger = logging.getLogger(__name__)

@contextmanager
def performance_monitor(operation_name: str, log_threshold: float = 0.5, monitor_memory: bool = True):
    """
    A context manager to monitor the performance of a block of code.

    Args:
        operation_name: A descriptive name for the operation being monitored.
        log_threshold: The minimum duration (in seconds) to log the performance.
        monitor_memory: Whether to monitor memory usage.
    """
    start_time = time.time()
    start_mem = memory_profiler.memory_usage() if monitor_memory else 0

    try:
        yield
    finally:
        duration = time.time() - start_time
        if duration >= log_threshold:
            if monitor_memory:
                end_mem = memory_profiler.memory_usage()
                mem_usage = end_mem - start_mem
                logger.info(
                    f"⏱️ Performance Monitor: {operation_name} took {duration:.2f}s, "
                    f"Memory Usage: {mem_usage:.2f} MB"
                )
            else:
                logger.info(
                    f"⏱️ Performance Monitor: {operation_name} took {duration:.2f}s"
                )

def profile_fn(log_threshold: float = 0.5, monitor_memory: bool = True):
    """
    A decorator to profile a function's execution time and memory usage.

    Args:
        log_threshold: The minimum duration (in seconds) to log the performance.
        monitor_memory: Whether to monitor memory usage.
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with performance_monitor(func.__name__, log_threshold, monitor_memory):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with performance_monitor(func.__name__, log_threshold, monitor_memory):
                return func(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator