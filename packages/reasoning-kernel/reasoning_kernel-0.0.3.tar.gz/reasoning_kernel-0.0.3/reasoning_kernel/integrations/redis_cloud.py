"""
Redis Cloud + RedisVL integration for Reasoning Kernel

This module provides integration with Redis Cloud using the official Redis Python client and RedisVL for vector search.
References:
- https://redis.io/docs/latest/operate/rc/rc-quickstart/
- https://github.com/redis/redis-vl-python

Environment variables required:
- REDIS_URL: Redis Cloud connection string

Usage:
    from reasoning_kernel.integrations.redis_cloud import get_redis_client, get_vector_index
    client = get_redis_client()
    index = get_vector_index(client, schema)
    ...
"""

import os
from redis import Redis
from redisvl.index import SearchIndex


def get_redis_client():
    """Return a Redis client using REDIS_URL from environment."""
    url = os.getenv("REDIS_URL")
    if not url:
        raise RuntimeError("REDIS_URL environment variable is not set.")
    return Redis.from_url(url)


def get_vector_index(client, schema: dict):
    """Return a RedisVL SearchIndex for the given schema and client."""
    return SearchIndex.from_dict(schema, redis_client=client, validate_on_load=True)
