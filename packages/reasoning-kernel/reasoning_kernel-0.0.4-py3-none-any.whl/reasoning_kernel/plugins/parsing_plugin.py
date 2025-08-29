"""
ParsingPlugin - Stage 1 of the Reasoning Kernel
===============================================

Transform natural language vignettes into structured constraints and formal representations.
Handles text parsing, constraint extraction, and structural analysis.
"""

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from semantic_kernel.functions import kernel_function
except Exception:
    # semantic_kernel is optional for import-time; provide type stubs
    def kernel_function(*args, **kwargs):
        def decorator(func):
            return func

        return decorator


try:
    import structlog

    logger = structlog.get_logger(__name__)
except Exception:
    # structlog is optional in some environments; fall back to stdlib logging
    import logging

    logger = logging.getLogger(__name__)


@dataclass
class ParsedConstraint:
    """A structured constraint extracted from text"""

    constraint_type: str  # "equality", "inequality", "temporal", "causal"
    variables: List[str]
    expression: str
    confidence: float
    source_text: str


@dataclass
class ParseResult:
    """Result from parsing operation"""

    success: bool
    constraints: List[ParsedConstraint]
    variables: List[str]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class ParsingPlugin:
    """
    Stage 1 Plugin: Transform vignettes into structured constraints.

    This plugin extracts formal constraints and variables from natural language
    descriptions, preparing them for knowledge retrieval and graph construction.
    """

    def __init__(self):
        """Initialize the parsing plugin"""
        self.variable_patterns = [
            r"\b([A-Z][a-zA-Z]*)\b",  # Capitalized words as variables
            r"\b(x|y|z|t|n|m|k|i|j)\b",  # Common mathematical variables
            r"\b(\w+)(?=\s*(?:=|>|<|≥|≤))",  # Words before operators
        ]

        self.constraint_patterns = {
            "equality": r"(\w+)\s*=\s*(\w+|\d+)",
            "inequality": r"(\w+)\s*(?:>|<|≥|≤)\s*(\w+|\d+)",
            "temporal": r"(\w+)\s*(?:before|after|during|when)\s*(\w+)",
            "causal": r"(\w+)\s*(?:causes?|leads? to|results? in)\s*(\w+)",
        }

    @kernel_function(
        description="Parse vignette text into structured constraints",
        name="parse_vignette",
    )
    async def parse_vignette(self, vignette: str) -> str:
        """
        Parse a vignette into structured constraints.

        Args:
            vignette: The natural language vignette to parse

        Returns:
            JSON string containing parsed constraints and variables
        """
        try:
            result = await self._parse_text(vignette)
            return json.dumps(
                {
                    "success": result.success,
                    "constraints": [
                        {
                            "type": c.constraint_type,
                            "variables": c.variables,
                            "expression": c.expression,
                            "confidence": c.confidence,
                            "source": c.source_text,
                        }
                        for c in result.constraints
                    ],
                    "variables": result.variables,
                    "metadata": result.metadata,
                    "error": result.error,
                }
            )
        except Exception as e:
            logger.error(f"Error parsing vignette: {e}")
            return json.dumps(
                {
                    "success": False,
                    "constraints": [],
                    "variables": [],
                    "metadata": {},
                    "error": str(e),
                }
            )

    async def _parse_text(self, text: str) -> ParseResult:
        """Internal method to parse text into constraints"""
        try:
            # Extract variables
            variables = self._extract_variables(text)

            # Extract constraints
            constraints = self._extract_constraints(text)

            # Generate metadata
            metadata = {
                "word_count": len(text.split()),
                "sentence_count": len(text.split(".")),
                "parsing_timestamp": "2025-08-25T11:30:00Z",
            }

            return ParseResult(
                success=True,
                constraints=constraints,
                variables=variables,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error in _parse_text: {e}")
            return ParseResult(
                success=False, constraints=[], variables=[], metadata={}, error=str(e)
            )

    def _extract_variables(self, text: str) -> List[str]:
        """Extract variable names from text"""
        variables = set()

        for pattern in self.variable_patterns:
            matches = re.findall(pattern, text)
            variables.update(matches)

        # Filter out common words that aren't variables
        stop_words = {
            "The",
            "A",
            "An",
            "This",
            "That",
            "These",
            "Those",
            "We",
            "They",
            "He",
            "She",
            "It",
            "You",
            "I",
        }
        variables = variables - stop_words

        return sorted(list(variables))

    def _extract_constraints(self, text: str) -> List[ParsedConstraint]:
        """Extract constraints from text"""
        constraints = []

        for constraint_type, pattern in self.constraint_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                constraint = ParsedConstraint(
                    constraint_type=constraint_type,
                    variables=[match.group(1), match.group(2)]
                    if len(match.groups()) >= 2
                    else [match.group(1)],
                    expression=match.group(0),
                    confidence=0.8,  # Default confidence
                    source_text=text[
                        max(0, match.start() - 20) : min(len(text), match.end() + 20)
                    ],
                )
                constraints.append(constraint)

        return constraints

    @kernel_function(
        description="Extract variables from text", name="extract_variables"
    )
    async def extract_variables(self, text: str) -> str:
        """Extract variables from text"""
        variables = self._extract_variables(text)
        return json.dumps({"variables": variables})

    @kernel_function(
        description="Extract constraints from text", name="extract_constraints"
    )
    async def extract_constraints(self, text: str) -> str:
        """Extract constraints from text"""
        constraints = self._extract_constraints(text)
        return json.dumps(
            {
                "constraints": [
                    {
                        "type": c.constraint_type,
                        "variables": c.variables,
                        "expression": c.expression,
                        "confidence": c.confidence,
                    }
                    for c in constraints
                ]
            }
        )


def create_parsing_plugin() -> ParsingPlugin:
    """Factory function to create a ParsingPlugin instance"""
    return ParsingPlugin()
