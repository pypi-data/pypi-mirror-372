from typing import Any, Dict
import logging
from semantic_kernel.processes.kernel_process.kernel_process_step import KernelProcessStep
from semantic_kernel.functions.kernel_function_decorator import kernel_function


class UnderstandStep(KernelProcessStep):
    """Understanding step for MSA process - extracts and structures reasoning task."""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.query = ""
        self.reasoning_type = ""
        self.complexity = ""
        self.understanding_result = {}

    @kernel_function(description="Process understanding phase of MSA pipeline", name="understand_query")
    async def understand_query(self, user_query: str) -> Dict[str, Any]:
        """Process understanding phase of MSA pipeline."""
        try:
            self.query = user_query

            # Basic understanding logic (will be enhanced with plugin integration)
            understanding_result = {
                "query": user_query,
                "reasoning_type": "general",
                "complexity": "medium",
                "extracted_concepts": self._extract_concepts(user_query),
                "reasoning_requirements": self._identify_requirements(user_query),
            }

            self.understanding_result = understanding_result
            self.reasoning_type = understanding_result.get("reasoning_type", "general")
            self.complexity = understanding_result.get("complexity", "medium")

            self.logger.info(f"Understanding completed for query: {user_query[:50]}...")

            return {
                "step": "understand",
                "status": "completed",
                "understanding": understanding_result,
                "reasoning_type": self.reasoning_type,
                "complexity": self.complexity,
            }

        except Exception as e:
            self.logger.error(f"Understanding step failed: {e}")

            return {"step": "understand", "status": "failed", "error": str(e), "understanding": None}

    def _extract_concepts(self, query: str) -> list:
        """Extract key concepts from query."""
        # Basic concept extraction (can be enhanced with NLP)
        import re

        # Simple word extraction
        words = re.findall(r"\b\w+\b", query.lower())
        # Filter out common stop words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
        }
        concepts = [word for word in words if word not in stop_words and len(word) > 2]

        return list(set(concepts))[:10]  # Return top 10 unique concepts

    def _identify_requirements(self, query: str) -> list:
        """Identify reasoning requirements from query."""
        requirements = []

        query_lower = query.lower()

        # Check for different types of reasoning requirements
        if any(word in query_lower for word in ["probability", "chance", "likely", "uncertain"]):
            requirements.append("probabilistic_reasoning")

        if any(word in query_lower for word in ["predict", "forecast", "future", "will"]):
            requirements.append("predictive_analysis")

        if any(word in query_lower for word in ["compare", "versus", "vs", "difference", "better"]):
            requirements.append("comparative_analysis")

        if any(word in query_lower for word in ["why", "because", "cause", "reason"]):
            requirements.append("causal_reasoning")

        if any(word in query_lower for word in ["optimize", "best", "maximum", "minimum", "improve"]):
            requirements.append("optimization")

        return requirements if requirements else ["general_reasoning"]
