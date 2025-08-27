"""
Daytona Cloud Integration for Reasoning Kernel

This module provides a real integration with Daytona Cloud using the official Daytona Python SDK.
References:
- https://github.com/daytonaio/docs/blob/main/src/content/docs/python-sdk/index.mdx
- https://github.com/daytonaio/docs/blob/main/public/llms.txt#_snippet_5

Environment variables required:
- DAYTONA_API_KEY: Your Daytona API key

Usage:
    from reasoning_kernel.integrations.daytona_cloud import get_daytona_sandbox, run_code_in_sandbox
    sandbox = get_daytona_sandbox()
    result = run_code_in_sandbox(sandbox, 'print("Hello from Daytona!")')
    print(result)
    sandbox.delete()
"""

import os
from daytona import Daytona, DaytonaConfig


def get_daytona_sandbox():
    """Create and return a Daytona sandbox using the API key from environment."""
    api_key = os.getenv("DAYTONA_API_KEY")
    if not api_key:
        raise RuntimeError("DAYTONA_API_KEY environment variable is not set.")
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)
    sandbox = daytona.create()
    return sandbox


def run_code_in_sandbox(sandbox, code: str):
    """Run Python code in the given Daytona sandbox and return the result."""
    response = sandbox.process.code_run(code)
    if response.exit_code != 0:
        raise RuntimeError(
            f"Daytona code execution failed: {response.exit_code} {response.result}"
        )
    return response.result
