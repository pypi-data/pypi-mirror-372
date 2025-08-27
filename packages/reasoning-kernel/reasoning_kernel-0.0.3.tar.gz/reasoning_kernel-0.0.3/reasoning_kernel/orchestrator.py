"""
Reasoning Kernel - Main Orchestrator
====================================

Implements the five-stage MSA pipeline:
1. Parse - Transform vignettes into structured constraints
2. Retrieve - Gather relevant background knowledge
3. Graph - Build causal dependency graphs
4. Synthesize - Generate probabilistic programs
5. Infer - Execute inference in secure sandbox

Integrates all plugins with error handling, retry logic, and comprehensive logging.
"""

import json
import time
from typing import Any, cast, Dict, List, Optional
from unittest.mock import MagicMock

from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
import structlog

from .plugins import InferencePlugin, KnowledgePlugin
from .utils.reasoning_chains import ReasoningChain
from .managers.thinking_mode_manager import ThinkingModeManager
from .managers.confidence_calculator import ConfidenceCalculator
from .builders.pipeline_payload_builder import PipelinePayloadBuilder
from .models.reasoning_types import (
    ReasoningConfig,
    ReasoningResult,
    CallbackBundle,
)

try:
    from .api.annotation_endpoints import manager as annotation_manager
except Exception:
    annotation_manager = None

logger = structlog.get_logger(__name__)


class ReasoningKernel:
    """
    Main orchestrator for the five-stage reasoning pipeline.
    """

    def __init__(self, kernel: Kernel, redis_client, config: Optional[ReasoningConfig] = None):
        self.kernel = kernel
        self.redis_client = redis_client
        self.config = config or ReasoningConfig()
        self.knowledge_plugin = KnowledgePlugin(redis_client)
        self.inference_plugin = InferencePlugin()
        self.thinking_mode_manager = ThinkingModeManager(self.config)
        self.confidence_calculator = ConfidenceCalculator()
        self.payload_builder = PipelinePayloadBuilder()

        if not isinstance(kernel, MagicMock):
            # self.msa_flow = create_msa_flow(self.kernel)
            pass

        logger.info("Reasoning Kernel initialized", config=self.config)

    async def run_causal_analysis(self, variables: List[str], data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run causal analysis using NumPyro."""
        try:
            causal_args = KernelArguments(variables=variables, data=data or {})
            result = await self.kernel.invoke(
                plugin_name="NumPyroReasoning", function_name="create_causal_model", arguments=causal_args
            )
            if result is None:
                return {}
            return cast(Any, result.value) if hasattr(result, "value") else cast(Any, result)
        except Exception as e:
            logger.error(f"Causal analysis failed: {e}")
            return {"error": str(e), "causal_model": None}

    async def quantify_uncertainty(self, scenario: str, variables: List[str]) -> Dict[str, Any]:
        """Quantify uncertainty in reasoning using Bayesian inference."""
        try:
            uncertainty_args = KernelArguments(scenario=scenario, variables=variables)
            result = await self.kernel.invoke(
                plugin_name="NumPyroReasoning", function_name="predict_with_uncertainty", arguments=uncertainty_args
            )
            if result is None:
                return {}
            return cast(Any, result.value) if hasattr(result, "value") else cast(Any, result)
        except Exception as e:
            logger.error(f"Uncertainty quantification failed: {e}")
            return {"error": str(e), "uncertainty": {}}

    async def reason_with_streaming(
        self,
        vignette: str,
        session_id: str,
        config: Optional[ReasoningConfig] = None,
        **kwargs,
    ) -> ReasoningResult:
        """Public streaming entrypoint delegating to unified pipeline."""
        self.config = config or self.config
        callbacks = CallbackBundle(**kwargs)
        return await self._run_pipeline(
            vignette=vignette,
            data=kwargs.get("data"),
            session_id=session_id,
            callbacks=callbacks,
            streaming=True,
        )

    async def reason(self, vignette: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> ReasoningResult:
        logger.info("Starting five-stage reasoning", vignette_length=len(vignette))
        return await self._run_pipeline(
            vignette=vignette,
            data=data,
            session_id=None,
            callbacks=CallbackBundle(),
            streaming=False,
        )

    async def _run_pipeline(
        self,
        vignette: str,
        data: Optional[Dict[str, Any]],
        session_id: Optional[str],
        callbacks: CallbackBundle,
        streaming: bool = False,
    ) -> ReasoningResult:
        logger.info("Running unified reasoning pipeline", session_id=session_id, streaming=streaming)
        chain = ReasoningChain(session_id=session_id)
        chain.start_reasoning(vignette, {"data_provided": data is not None})
        result = ReasoningResult(reasoning_chain=chain)
        start_time = time.time()

        try:
            pipeline_result = await self.unified_pipeline.execute(
                scenario=vignette,
                session_id=session_id,
                user_context=data,
            )
            result.success = pipeline_result.status == "completed"
            result.inference_result = pipeline_result.final_result
            result.error_message = pipeline_result.error
            result.total_execution_time = time.time() - start_time
            result.overall_confidence = self.confidence_calculator.calculate_overall_confidence(result)
            chain.complete_reasoning(
                {"success": result.success, "total_time": result.total_execution_time, "confidence": result.overall_confidence},
                result.total_execution_time,
            )
            logger.info("Unified reasoning completed", success=result.success, confidence=result.overall_confidence, total_time=result.total_execution_time)
            return result
        except Exception as e:
            result.error_message = str(e)
            result.total_execution_time = time.time() - start_time
            result.success = False
            chain.complete_reasoning({"success": False, "error": str(e)}, result.total_execution_time)
            logger.error("Unified reasoning failed", error=str(e), execution_time=result.total_execution_time)
            return result

    async def get_reasoning_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of ongoing reasoning process"""
        try:
            status_key = f"reasoning:status:{session_id}"
            status_data = await self.redis_client.get(status_key)
            if status_data:
                return json.loads(status_data)
            return {"status": "not_found"}
        except Exception as e:
            logger.error("Failed to get reasoning status", error=str(e))
            return {"status": "error", "message": str(e)}

    async def cancel_reasoning(self, session_id: str) -> bool:
        """Cancel ongoing reasoning process"""
        try:
            status_key = f"reasoning:status:{session_id}"
            await self.redis_client.set(status_key, json.dumps({"status": "cancelled"}))
            logger.info("Reasoning cancelled", session_id=session_id)
            return True
        except Exception as e:
            logger.error("Failed to cancel reasoning", error=str(e))
            return False