"""
MSA (Modular Semantic Architecture) API endpoints for the reasoning pipeline.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from reasoning_kernel.semantic_kernel_integration.kernel_factory import create_kernel_with_plugins
from reasoning_kernel.msa_processes.msa_pipeline_process import MSAPipelineProcess

router = APIRouter()

# Create kernel instance (could be cached or managed differently in production)
kernel = create_kernel_with_plugins()

@router.post("/api/v1/msa/reason")
async def run_msa_reasoning_pipeline(scenario: str) -> Dict[str, Any]:
    """
    Run the complete MSA reasoning pipeline on a given scenario.
    
    Args:
        scenario: The input scenario text to process
        
    Returns:
        Dictionary containing the pipeline results including:
        - comprehension: Understanding phase results
        - search_results: Knowledge retrieval results
        - dependency_graph: Inference graph structure
        - numpyro_program: Generated NumPyro program code
    """
    try:
        # Create MSA pipeline process
        pipeline_process = MSAPipelineProcess()
        process = pipeline_process.create_process()
        
        # Initialize context with scenario
        initial_context = {"scenario": scenario}
        
        # Execute the process
        result_context = await process.execute(initial_context)
        
        # Extract and return relevant results
        return {
            "comprehension": result_context.get("comprehension", {}),
            "search_results": result_context.get("search_results", {}),
            "dependency_graph": result_context.get("dependency_graph", {}),
            "numpyro_program": result_context.get("numpyro_program", {}),
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MSA pipeline execution failed: {str(e)}")

@router.get("/api/v1/msa/health")
async def msa_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for MSA components.
    """
    try:
        # Basic health check - verify kernel and plugins are available
        plugins = kernel.get_plugins()
        plugin_names = list(plugins.keys()) if plugins else []
        
        return {
            "status": "healthy",
            "plugins_available": plugin_names,
            "kernel_initialized": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MSA health check failed: {str(e)}")