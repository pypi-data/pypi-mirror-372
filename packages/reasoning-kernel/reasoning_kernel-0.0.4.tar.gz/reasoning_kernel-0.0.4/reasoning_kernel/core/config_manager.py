"""
Configuration manager for the Reasoning Kernel.

This module provides factory functions for creating and managing configuration instances,
replacing the global singleton pattern with a more testable and flexible approach.
"""
import os
from typing import Optional, Dict, Any
from functools import lru_cache

from .settings import Settings


# Global cache for configuration instances
_config_cache: Dict[str, Settings] = {}


def get_config(**overrides) -> Settings:
    """
    Create a new Settings instance with optional overrides.

    Args:
        **overrides: Keyword arguments to override default settings.

    Returns:
        A new Settings instance.
    """
    return Settings(**overrides)


@lru_cache(maxsize=1)
def get_cached_config() -> Settings:
    """
    Get a cached Settings instance for performance.

    This uses LRU caching to avoid recreating the same instance repeatedly.

    Returns:
        A cached Settings instance.
    """
    return Settings()


def get_environment_config(env: Optional[str] = None) -> Settings:
    """
    Load configuration based on the specified environment.

    Args:
        env: Environment name (e.g., 'development', 'test', 'production').
             If None, uses the current environment.

    Returns:
        A Settings instance configured for the environment.
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")
    
    # Environment-specific overrides
    overrides = {}
    if env == "test":
        overrides.update({
            "log_level": "DEBUG",
            "redis_url": "redis://test:6379/0"
        })
    elif env == "production":
        overrides.update({
            "log_level": "WARNING",
            "redis_url": "redis://production:6379/0"
        })
    
    return Settings(**overrides)


def get_service_config(service_name: str) -> Settings:
    """
    Get configuration for a specific service.

    Args:
        service_name: Name of the service.

    Returns:
        A Settings instance with service-specific configuration.
    """
    # Service-specific environment variables
    prefix = f"{service_name.upper()}_"
    overrides = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            overrides[config_key] = value
    
    return Settings(**overrides)


def clear_config_cache() -> None:
    """
    Clear the configuration cache.

    This is useful for testing to ensure fresh configuration instances.
    """
    global _config_cache
    _config_cache = {}
    get_cached_config.cache_clear()


# Test utilities
def get_test_config(**overrides) -> Settings:
    """
    Get a configuration instance for testing.

    Args:
        **overrides: Additional overrides for test configuration.

    Returns:
        A Settings instance configured for testing.
    """
    test_defaults = {
        "log_level": "DEBUG",
        "redis_url": "redis://test:6379/0",
        "openai_model": "gpt-4-test",
        "max_reasoning_steps": 50,
        "probabilistic_samples": 100,
        "uncertainty_threshold": 0.1
    }
    test_defaults.update(overrides)
    return Settings(**test_defaults)