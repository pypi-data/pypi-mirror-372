from typing import Any, Dict, Optional
import logging
from semantic_kernel import Kernel
from semantic_kernel.processes.kernel_process import KernelProcess
from semantic_kernel.processes.process_builder import ProcessBuilder

# Import process steps
from .steps.understand_step import UnderstandStep
from .steps.search_step import SearchStep
from .steps.infer_step import InferStep
from .steps.synthesize_step import SynthesizeStep


class MSAPipelineProcess:
    """MSA Pipeline implemented as a Semantic Kernel Process Framework."""

    def __init__(self, kernel: Optional[Kernel] = None):
        self.kernel = kernel
        self._logger = logging.getLogger(__name__)
        self.process = None

    def create_process(self, process_name: str = "MSA_Pipeline") -> KernelProcess:
        """Build the MSA pipeline process using SK Process Framework."""
        try:
            # Create process builder with proper namespace
            process_builder = ProcessBuilder(name=process_name, event_namespace="msa")

            # Add process steps
            self._logger.info("Adding process steps for MSA Reasoning Pipeline")
            understand_step = process_builder.add_step(UnderstandStep, name="understand")
            search_step = process_builder.add_step(SearchStep, name="search")
            infer_step = process_builder.add_step(InferStep, name="infer")
            synthesize_step = process_builder.add_step(SynthesizeStep, name="synthesize")

            # Define process flow with proper event routing
            # Entry point: Start with understanding
            process_builder.on_input_event("StartEvent").send_event_to(understand_step)

            # Step 1: Understanding -> Search (when understanding completes)
            understand_step.on_event("UnderstandingComplete").send_event_to(search_step)

            # Step 2: Search -> Inference (when search completes)
            search_step.on_event("SearchComplete").send_event_to(infer_step)

            # Step 3: Inference -> Synthesis (when inference completes)
            infer_step.on_event("InferenceComplete").send_event_to(synthesize_step)

            # Step 4: Synthesis -> Process completion
            synthesize_step.on_event("SynthesisComplete").stop_process()

            # Build the process
            self.process = process_builder.build()

            self._logger.info(f"MSA Pipeline process '{process_name}' built successfully")
            return self.process

        except Exception as e:
            self._logger.error(f"Failed to build MSA process: {e}")
            raise

    async def run_pipeline(self, user_query: str) -> Dict[str, Any]:
        """Execute the complete MSA pipeline with simplified step execution."""
        try:
            self._logger.info(f"Starting MSA pipeline for query: {user_query[:100]}...")

            # Execute steps sequentially (simplified approach for demonstration)
            pipeline_results = {}

            # Step 1: Understanding
            understand_step = UnderstandStep()
            understanding_result = await understand_step.understand_query(user_query)
            pipeline_results["understand"] = understanding_result

            if understanding_result.get("status") != "completed":
                return self._create_error_result("Understanding step failed", pipeline_results)

            # Step 2: Search
            search_step = SearchStep()
            search_result = await search_step.search_knowledge(understanding_result["understanding"])
            pipeline_results["search"] = search_result

            if search_result.get("status") != "completed":
                return self._create_error_result("Search step failed", pipeline_results)

            # Step 3: Inference
            infer_step = InferStep()
            inference_result = await infer_step.build_inference(
                understanding_result["understanding"], search_result["search_results"]
            )
            pipeline_results["infer"] = inference_result

            if inference_result.get("status") != "completed":
                return self._create_error_result("Inference step failed", pipeline_results)

            # Step 4: Synthesis
            synthesize_step = SynthesizeStep()
            synthesis_result = await synthesize_step.synthesize_results(
                understanding_result["understanding"],
                search_result["search_results"],
                {
                    "dependency_graph": inference_result["dependency_graph"],
                    "probabilistic_relationships": inference_result["probabilistic_relationships"],
                    "inference_model": inference_result["inference_model"],
                },
            )
            pipeline_results["synthesize"] = synthesis_result

            # Create comprehensive result
            final_result = self._create_success_result(user_query, pipeline_results, synthesis_result)

            self._logger.info("MSA pipeline execution completed successfully")
            return final_result

        except Exception as e:
            self._logger.error(f"MSA pipeline execution failed: {e}")
            return self._create_error_result(f"Pipeline execution failed: {str(e)}", {})

    def _create_success_result(self, query: str, pipeline_results: Dict, synthesis_result: Dict) -> Dict[str, Any]:
        """Create a comprehensive success result."""
        return {
            "status": "completed",
            "query": query,
            "pipeline_results": pipeline_results,
            "final_answer": synthesis_result.get("synthesis_result", {}),
            "metadata": {
                "execution_steps": len(pipeline_results),
                "reasoning_type": pipeline_results.get("understand", {}).get("reasoning_type", "general"),
                "confidence": synthesis_result.get("confidence", 0.5),
                "has_program": synthesis_result.get("has_program", False),
            },
            "summary": {
                "understanding": pipeline_results.get("understand", {}).get("understanding", {}),
                "search_results_count": len(
                    pipeline_results.get("search", {}).get("search_results", {}).get("documents", [])
                ),
                "inference_nodes": pipeline_results.get("infer", {}).get("nodes_count", 0),
                "synthesis_confidence": synthesis_result.get("confidence", 0.5),
            },
        }

    def _create_error_result(self, error_message: str, partial_results: Dict) -> Dict[str, Any]:
        """Create an error result with partial pipeline results."""
        return {
            "status": "failed",
            "error": error_message,
            "partial_results": partial_results,
            "final_answer": None,
            "metadata": {
                "completed_steps": len(partial_results),
                "failed_at": self._determine_failure_step(partial_results),
            },
        }

    def _determine_failure_step(self, partial_results: Dict) -> str:
        """Determine which step the pipeline failed at."""
        if "synthesize" in partial_results:
            return "synthesis"
        elif "infer" in partial_results:
            return "inference"
        elif "search" in partial_results:
            return "search"
        elif "understand" in partial_results:
            return "understanding"
        else:
            return "initialization"

    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the current process."""
        if self.process:
            return {
                "process_name": getattr(self.process, "name", "MSA_Pipeline"),
                "has_kernel": self.kernel is not None,
                "process_built": self.process is not None,
            }
        return {"process_name": "MSA_Pipeline", "has_kernel": self.kernel is not None, "process_built": False}
