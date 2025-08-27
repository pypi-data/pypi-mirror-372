# -*- coding: utf-8 -*-
"""
Core components for token management, cost estimation, and budget control.

This module provides a framework for tracking token usage across different LLM
providers, estimating costs based on configurable pricing models, and enforcing
usage limits to prevent budget overruns.

Key Features:
- **Token Counting:** A flexible `TokenCounter` class that can be extended to
  support different tokenization strategies (e.g., tiktoken, sentencepiece).
- **Cost Estimation:** A `CostEstimator` that calculates the cost of LLM
  operations based on token counts and provider-specific pricing.
- **Budget Management:** A `TokenBudgetManager` that tracks token usage against
  predefined limits and provides alerts when thresholds are exceeded.
- **Integration with Semantic Kernel:** The components are designed to be
  easily integrated into the `KernelManager` and other parts of the reasoning
  kernel.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict

logger = logging.getLogger(__name__)


class TokenCounter(ABC):
    """Abstract base class for token counters."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a given text."""
        pass


class TiktokenCounter(TokenCounter):
    """A token counter that uses the tiktoken library."""

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the TiktokenCounter.

        Args:
            model_name: The name of the model to use for tokenization.
        """
        try:
            import tiktoken
        except ImportError:
            raise ImportError(
                "The 'tiktoken' library is required for TiktokenCounter. "
                "Please install it with 'pip install tiktoken'."
            )
        self.encoding = tiktoken.encoding_for_model(model_name)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a given text."""
        return len(self.encoding.encode(text))


class CostEstimator:
    """Estimates the cost of LLM operations based on token counts."""

    def __init__(self, pricing_info: Dict[str, Dict[str, float]]):
        """
        Initialize the CostEstimator.

        Args:
            pricing_info: A dictionary containing the pricing information for
                different models. The format is:
                {
                    "model_name": {
                        "prompt_tokens": cost_per_1k_prompt_tokens,
                        "completion_tokens": cost_per_1k_completion_tokens,
                    }
                }
        """
        self.pricing_info = pricing_info

    def estimate_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """
        Estimate the cost of an LLM operation.

        Args:
            model_name: The name of the model used for the operation.
            prompt_tokens: The number of prompt tokens.
            completion_tokens: The number of completion tokens.

        Returns:
            The estimated cost of the operation.
        """
        if model_name not in self.pricing_info:
            logger.warning(f"Pricing information not found for model: {model_name}")
            return 0.0

        pricing = self.pricing_info[model_name]
        prompt_cost = (prompt_tokens / 1000) * pricing.get("prompt_tokens", 0.0)
        completion_cost = (completion_tokens / 1000) * pricing.get(
            "completion_tokens", 0.0
        )
        return prompt_cost + completion_cost


class TokenBudgetManager:
    """Manages token usage against a predefined budget."""

    def __init__(self, budget: float, alert_threshold: float = 0.8):
        """
        Initialize the TokenBudgetManager.

        Args:
            budget: The total token budget.
            alert_threshold: The usage threshold at which to trigger an alert.
        """
        self.budget = budget
        self.alert_threshold = alert_threshold
        self.usage: float = 0.0

    def update_usage(self, tokens_used: int) -> None:
        """
        Update the token usage and check if the budget has been exceeded.

        Args:
            tokens_used: The number of tokens used in the latest operation.
        """
        self.usage += tokens_used
        if self.usage >= self.budget * self.alert_threshold:
            logger.warning(
                f"Token usage ({self.usage}) has exceeded the alert "
                f"threshold of {self.alert_threshold * 100}% of the budget "
                f"({self.budget})."
            )

    def has_budget_exceeded(self) -> bool:
        """Check if the token budget has been exceeded."""
        return self.usage >= self.budget

    def get_usage_percentage(self) -> float:
        """Get the current token usage as a percentage of the budget."""
        if self.budget == 0:
            return 0.0
        return (self.usage / self.budget) * 100