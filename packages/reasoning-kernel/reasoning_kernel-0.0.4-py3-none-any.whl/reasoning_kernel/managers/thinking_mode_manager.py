"""
The `ThinkingModeManager` class orchestrates the generation of human-readable explanations for the reasoning process. When enabled, it produces a narrative that details the step-by-step thinking of the system. This can be delivered in two ways: as a real-time stream of thoughts for immediate feedback or as a comprehensive, detailed analysis after the reasoning is complete. The manager constructs a sequence of thoughts based on the completed reasoning stages, providing transparency into how the system arrived at its conclusions.
"""
import asyncio
from typing import List

import structlog

from ..utils.reasoning_chains import ReasoningChain
from ..reasoning_kernel import ReasoningResult, ReasoningConfig, CallbackBundle

logger = structlog.get_logger(__name__)


class ThinkingModeManager:
    def __init__(self, config: ReasoningConfig):
        self.config = config

    async def handle_thinking_mode(
        self,
        result: ReasoningResult,
        vignette: str,
        chain: ReasoningChain,
        callbacks: CallbackBundle,
        streaming: bool,
    ):
        """Handle thinking mode output generation."""
        if streaming and callbacks.on_thinking_sentence:
            await self._generate_streaming_thoughts(result, vignette, chain, callbacks.on_thinking_sentence)
        else:
            await self._generate_thinking_output(result, vignette, chain)

    async def _generate_streaming_thoughts(
        self, result: ReasoningResult, vignette: str, chain: ReasoningChain, on_thinking_sentence
    ):
        """Generate natural language thinking sentences in real-time for streaming mode."""
        if not on_thinking_sentence:
            return

        thoughts = self._build_thought_sequence(result, vignette)

        # Stream thoughts with delays for natural pacing
        for thought in thoughts:
            await on_thinking_sentence(thought)
            await asyncio.sleep(0.5)  # Natural pacing

    def _build_thought_sequence(self, result: ReasoningResult, vignette: str) -> List[str]:
        """Build a sequence of thinking thoughts based on reasoning stages completed."""
        thoughts = [
            "Let me analyze this scenario step by step using probabilistic reasoning...",
            f"The key question here involves understanding {vignette[:50]}...",
            "I'll need to model the uncertainty and causal relationships involved.",
        ]

        # Add stage-specific thoughts
        if result.parsed_vignette:
            thoughts.append("I've identified the main entities and constraints that define this problem space.")

        if result.retrieval_context:
            thoughts.append("My knowledge base provides relevant context from similar scenarios.")

        if result.dependency_graph:
            thoughts.append("The causal structure reveals how different factors influence each other.")

        if result.probabilistic_program:
            thoughts.append("I've constructed a probabilistic model to quantify the uncertainties.")

        if result.inference_result:
            thoughts.append("The Bayesian inference results provide probability distributions for key outcomes.")

        thoughts.append(
            f"Based on this cognitive modeling, I can provide insights with {result.overall_confidence:.0%} confidence."
        )

        return thoughts

    async def _generate_thinking_output(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate sentence-based thinking process and reasoning output"""
        if not self.config.enable_thinking_mode:
            return

        logger.info("Generating thinking mode output", detail_level=self.config.thinking_detail_level)

        # Initialize thinking outputs
        result.thinking_process = []
        result.reasoning_sentences = []
        result.step_by_step_analysis = {}

        try:
            # Generate overall reasoning narrative
            if self.config.generate_reasoning_sentences:
                await self._generate_reasoning_sentences(result, vignette, chain)

            # Generate step-by-step thinking analysis
            if self.config.include_step_by_step_thinking:
                await self._generate_step_by_step_analysis(result, vignette, chain)

            # Generate thinking process summary
            await self._generate_thinking_summary(result, vignette, chain)

            logger.info(
                "Thinking mode output generated successfully",
                sentences_count=len(result.reasoning_sentences),
                thinking_steps=len(result.thinking_process),
            )

        except Exception as e:
            logger.error("Failed to generate thinking output", error=str(e))
            # Provide fallback thinking output
            result.thinking_process = [
                f"I'm analyzing the scenario: {vignette[:100]}...",
                "Processing the information through multiple reasoning stages...",
                f"Generated insights with {result.overall_confidence:.2f} confidence level.",
            ]

    async def _generate_reasoning_sentences(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate coherent reasoning sentences that explain the thinking process"""

        reasoning_sentences = []

        # Analyze what we've learned at each stage
        if result.parsed_vignette:
            entities_count = getattr(result.parsed_vignette, "entities_count", 0)
            constraints_count = getattr(result.parsed_vignette, "constraints_count", 0)
            reasoning_sentences.append(
                f"I began by parsing the scenario and identified {entities_count} key entities and {constraints_count} important constraints that shape this situation."
            )

        if result.retrieval_context:
            docs_count = len(getattr(result.retrieval_context, "documents", []))
            reasoning_sentences.append(
                f"I then searched my knowledge base and found {docs_count} relevant documents that provide background context for this type of scenario."
            )

        if result.dependency_graph:
            nodes_count = getattr(result.dependency_graph, "nodes_count", 0)
            edges_count = getattr(result.dependency_graph, "edges_count", 0)
            reasoning_sentences.append(
                f"Next, I built a causal dependency graph with {nodes_count} factors and {edges_count} relationships to understand how different elements influence each other."
            )

        if result.probabilistic_program:
            variables_count = getattr(result.probabilistic_program, "variables_count", 0)
            reasoning_sentences.append(
                f"I synthesized this knowledge into a probabilistic model with {variables_count} variables that can quantify uncertainty and make predictions."
            )

        if result.inference_result:
            samples_count = getattr(result.inference_result, "num_samples", 0)
            params_count = len(getattr(result.inference_result, "posterior_samples", {}))
            reasoning_sentences.append(
                f"Finally, I ran Bayesian inference with {samples_count} samples to estimate {params_count} key parameters and their probability distributions."
            )

        # Add confidence assessment
        confidence_level = (
            "high" if result.overall_confidence > 0.8 else "moderate" if result.overall_confidence > 0.6 else "limited"
        )
        reasoning_sentences.append(
            f"Based on this analysis, I have {confidence_level} confidence (score: {result.overall_confidence:.2f}) in these conclusions."
        )

        # Add insights based on detail level
        if self.config.thinking_detail_level == "detailed":
            reasoning_sentences.extend(
                [
                    "The scenario involves complex interactions between multiple factors, requiring careful probabilistic reasoning.",
                    "Key uncertainties have been identified and quantified to provide actionable insights.",
                    f"This analysis took {result.total_execution_time:.1f} seconds across {len(result.stage_timings or {})} reasoning stages.",
                ]
            )
        elif self.config.thinking_detail_level == "moderate":
            reasoning_sentences.append(
                "The analysis reveals important patterns and relationships that inform decision-making."
            )

        result.reasoning_sentences = reasoning_sentences

    async def _generate_step_by_step_analysis(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate detailed step-by-step analysis for each stage"""

        step_analysis = {}

        # Parse stage analysis
        if result.parsed_vignette:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["parse"] = [
                "I started by carefully reading and parsing the scenario text.",
                "Extracted key entities and identified their roles and relationships.",
                "Found constraints and limitations that affect possible outcomes.",
                f"This parsing stage completed in {timings.get('parse', 0):.2f} seconds with {confs.get('parse', 0):.2f} confidence.",
            ]

        # Retrieve stage analysis
        if result.retrieval_context:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["retrieve"] = [
                "I searched my knowledge base for similar scenarios and relevant information.",
                "Retrieved background knowledge about the domain and context.",
                "Cross-referenced findings with established patterns and research.",
                f"Knowledge retrieval took {timings.get('retrieve', 0):.2f} seconds with {confs.get('retrieve', 0):.2f} confidence.",
            ]

        # Graph stage analysis
        if result.dependency_graph:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["graph"] = [
                "I constructed a causal dependency graph to model factor interactions.",
                "Identified direct and indirect causal relationships between variables.",
                "Analyzed feedback loops and emergent dependencies.",
                f"Graph generation completed in {timings.get('graph', 0):.2f} seconds with {confs.get('graph', 0):.2f} confidence.",
            ]

        # Synthesis stage analysis
        if result.probabilistic_program:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["synthesize"] = [
                "I synthesized the knowledge into a custom probabilistic model.",
                "Defined probability distributions for uncertain variables.",
                "Specified causal relationships and conditional dependencies.",
                f"Model synthesis took {timings.get('synthesize', 0):.2f} seconds with {confs.get('synthesize', 0):.2f} confidence.",
            ]

        # Inference stage analysis
        if result.inference_result:
            timings = result.stage_timings or {}
            confs = result.stage_confidences or {}
            step_analysis["infer"] = [
                "I ran Bayesian inference to estimate parameter distributions.",
                "Generated posterior samples using Monte Carlo methods.",
                "Computed credible intervals and statistical summaries.",
                f"Inference completed in {timings.get('infer', 0):.2f} seconds with {confs.get('infer', 0):.2f} confidence.",
            ]

        result.step_by_step_analysis = step_analysis

    async def _generate_thinking_summary(self, result: ReasoningResult, vignette: str, chain: ReasoningChain):
        """Generate overall thinking process summary"""
        thinking_steps: List[str] = []

        # High-level reasoning approach
        thinking_steps.append("I approached this scenario using a systematic five-stage reasoning pipeline.")

        # Identify key challenges
        if result.overall_confidence < 0.7:
            thinking_steps.append(
                "I encountered some uncertainty in this analysis due to limited information or complex interactions."
            )
        else:
            thinking_steps.append(
                "I was able to analyze this scenario with good confidence given the available information."
            )

        # Describe reasoning strategy
        stage_timings = result.stage_timings or {}
        stages_completed = len([s for s in stage_timings.keys() if stage_timings.get(s, 0) > 0])
        if stages_completed >= 4:
            thinking_steps.append(
                "I completed a comprehensive analysis including knowledge extraction, causal modeling, and probabilistic inference."
            )
        elif stages_completed >= 2:
            thinking_steps.append(
                "I completed the initial analysis stages and extracted key insights from the available information."
            )
        else:
            thinking_steps.append(
                "I began the analysis but encountered limitations that prevented full reasoning completion."
            )

        # Highlight key insights
        if result.dependency_graph and hasattr(result.dependency_graph, "key_insights"):
            thinking_steps.append("The most important insight is understanding how the key factors interact causally.")

        # Decision-making guidance
        if result.inference_result:
            thinking_steps.append(
                "The probabilistic analysis provides quantified guidance for decision-making under uncertainty."
            )

        # Meta-cognitive reflection
        thinking_steps.append(
            "This reasoning process demonstrates how I systematically break down complex scenarios into manageable components."
        )

        result.thinking_process = thinking_steps