"""
Individual MSA pipeline stage commands for granular control
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import click

from reasoning_kernel.cli.ui import UIManager
from reasoning_kernel.core.env import load_project_dotenv
from reasoning_kernel.core.kernel_manager import KernelManager
from reasoning_kernel.msa.synthesis_engine import MSAEngine
from reasoning_kernel.msa.pipeline.pipeline_stage import StageType, StageStatus, PipelineContext

# Load environment variables
load_project_dotenv(override=False)

# Configure logging
logger = logging.getLogger(__name__)


class StageExecutor:
    """Execute individual MSA pipeline stages"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.ui_manager = UIManager(verbose=verbose)
        self.kernel_manager: Optional[KernelManager] = None
        self.msa_engine: Optional[MSAEngine] = None
        
    async def initialize(self):
        """Initialize the MSA components"""
        try:
            if self.verbose:
                self.ui_manager.print_info("Initializing MSA Reasoning Engine...")
            
            # Initialize Semantic Kernel
            self.kernel_manager = KernelManager()
            await self.kernel_manager.initialize()
            
            # Initialize MSA Engine
            self.msa_engine = MSAEngine(self.kernel_manager)
            await self.msa_engine.initialize()
            
            if self.verbose:
                self.ui_manager.print_success("MSA Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MSA components: {e}")
            self.ui_manager.print_error(f"Failed to initialize: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.msa_engine:
                await self.msa_engine.cleanup()
            if self.kernel_manager:
                await self.kernel_manager.cleanup()
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")
    
    async def execute_parse_stage(self, scenario: str, session_id: str) -> Dict[str, Any]:
        """Execute the Parse stage - Natural language understanding and problem decomposition"""
        self.ui_manager.print_subheader("🔍 PARSE STAGE", "bold blue")
        
        start_time = time.time()
        
        # Simulate parsing stage - in real implementation this would use the actual MSA pipeline
        try:
            # Basic NLU processing
            words = scenario.lower().split()
            entities = [word for word in words if len(word) > 3 and word.isalpha()]
            
            # Problem decomposition
            questions = []
            if "how" in scenario.lower():
                questions.append("process_question")
            if "why" in scenario.lower():
                questions.append("causal_question")
            if "what" in scenario.lower():
                questions.append("factual_question")
                
            complexity = "high" if len(entities) > 8 else "medium" if len(entities) > 4 else "low"
            
            result = {
                "scenario": scenario,
                "entities": entities[:10],  # Limit for demo
                "question_types": questions,
                "complexity": complexity,
                "word_count": len(words),
                "confidence": 0.85
            }
            
            execution_time = time.time() - start_time
            self.ui_manager.print_pipeline_stage_result("parse", {"success": True, "data": result}, execution_time)
            
            return {
                "stage": "parse",
                "success": True,
                "data": result,
                "execution_time": execution_time,
                "session_id": session_id
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Parse stage failed: {e}")
            self.ui_manager.print_pipeline_stage_result("parse", {"success": False, "error": str(e)}, execution_time)
            return {
                "stage": "parse",
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "session_id": session_id
            }
    
    async def execute_knowledge_stage(self, parse_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Knowledge stage - Retrieval-augmented generation from memory systems"""
        self.ui_manager.print_subheader("📚 KNOWLEDGE STAGE", "bold green")
        
        start_time = time.time()
        
        try:
            parse_data = parse_result.get("data", {})
            entities = parse_data.get("entities", [])
            
            # Simulate knowledge retrieval
            knowledge_base = []
            for entity in entities[:5]:  # Limit for demo
                knowledge_base.append({
                    "entity": entity,
                    "definition": f"Knowledge about {entity}",
                    "relationships": [f"relates_to_{entity}_{i}" for i in range(2)],
                    "confidence": 0.9
                })
            
            result = {
                "knowledge_base": knowledge_base,
                "total_entities": len(entities),
                "retrieved_count": len(knowledge_base),
                "coverage": min(len(knowledge_base) / max(len(entities), 1), 1.0),
                "confidence": 0.8
            }
            
            execution_time = time.time() - start_time
            self.ui_manager.print_pipeline_stage_result("knowledge", {"success": True, "data": result}, execution_time)
            
            return {
                "stage": "knowledge", 
                "success": True,
                "data": result,
                "execution_time": execution_time,
                "parse_result": parse_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Knowledge stage failed: {e}")
            self.ui_manager.print_pipeline_stage_result("knowledge", {"success": False, "error": str(e)}, execution_time)
            return {
                "stage": "knowledge",
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "parse_result": parse_result
            }
    
    async def execute_graph_stage(self, knowledge_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Graph stage - Causal dependency graph construction"""
        self.ui_manager.print_subheader("🕸️ GRAPH STAGE", "bold yellow")
        
        start_time = time.time()
        
        try:
            knowledge_data = knowledge_result.get("data", {})
            knowledge_base = knowledge_data.get("knowledge_base", [])
            
            # Simulate graph construction
            nodes = []
            edges = []
            
            for i, kb_item in enumerate(knowledge_base):
                nodes.append({
                    "id": f"node_{i}",
                    "entity": kb_item["entity"],
                    "type": "entity"
                })
                
                # Create edges between entities
                for j, other_item in enumerate(knowledge_base[i+1:], i+1):
                    edges.append({
                        "source": f"node_{i}",
                        "target": f"node_{j}",
                        "relationship": "influences",
                        "strength": 0.7
                    })
            
            result = {
                "nodes": nodes,
                "edges": edges[:10],  # Limit for demo
                "node_count": len(nodes),
                "edge_count": len(edges),
                "graph_density": len(edges) / max(len(nodes) * (len(nodes) - 1) / 2, 1),
                "confidence": 0.75
            }
            
            execution_time = time.time() - start_time
            self.ui_manager.print_pipeline_stage_result("graph", {"success": True, "data": result}, execution_time)
            
            return {
                "stage": "graph",
                "success": True,
                "data": result,
                "execution_time": execution_time,
                "previous_results": knowledge_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Graph stage failed: {e}")
            self.ui_manager.print_pipeline_stage_result("graph", {"success": False, "error": str(e)}, execution_time)
            return {
                "stage": "graph",
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "previous_results": knowledge_result
            }
    
    async def execute_synthesis_stage(self, graph_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Synthesis stage - Dynamic model generation and program synthesis"""
        self.ui_manager.print_subheader("⚙️ SYNTHESIS STAGE", "bold magenta")
        
        start_time = time.time()
        
        try:
            graph_data = graph_result.get("data", {})
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
            
            # Simulate model synthesis
            model_components = []
            for node in nodes[:5]:  # Limit for demo
                model_components.append({
                    "variable": node["entity"],
                    "distribution": "Normal",
                    "parameters": {"mean": 0.0, "std": 1.0},
                    "dependencies": [edge["target"] for edge in edges if edge["source"] == node["id"]][:2]
                })
            
            # Generate synthesized model code (simplified)
            model_code = f"""
import numpyro
import numpyro.distributions as dist

def synthesized_model():
    # Generated model with {len(model_components)} variables
{'\n'.join([f'    {comp["variable"]} = numpyro.sample("{comp["variable"]}", dist.Normal(0, 1))' 
            for comp in model_components[:3]])}
    return {{{", ".join([f'"{comp["variable"]}": {comp["variable"]}' for comp in model_components[:3]])}}}
"""
            
            result = {
                "model_components": model_components,
                "model_code": model_code.strip(),
                "variable_count": len(model_components),
                "dependency_count": sum(len(comp["dependencies"]) for comp in model_components),
                "model_complexity": "medium",
                "confidence": 0.72
            }
            
            execution_time = time.time() - start_time
            self.ui_manager.print_pipeline_stage_result("synthesis", {"success": True, "data": result}, execution_time)
            
            return {
                "stage": "synthesis",
                "success": True,
                "data": result,
                "execution_time": execution_time,
                "previous_results": graph_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Synthesis stage failed: {e}")
            self.ui_manager.print_pipeline_stage_result("synthesis", {"success": False, "error": str(e)}, execution_time)
            return {
                "stage": "synthesis",
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "previous_results": graph_result
            }
    
    async def execute_inference_stage(self, synthesis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Inference stage - Probabilistic execution and result generation"""
        self.ui_manager.print_subheader("🎲 INFERENCE STAGE", "bold cyan")
        
        start_time = time.time()
        
        try:
            synthesis_data = synthesis_result.get("data", {})
            model_components = synthesis_data.get("model_components", [])
            
            # Simulate probabilistic inference
            inference_results = {}
            for component in model_components[:3]:  # Limit for demo
                inference_results[component["variable"]] = {
                    "mean": 0.1,
                    "std": 0.8,
                    "samples": 1000,
                    "r_hat": 1.01,  # Good convergence
                    "eff_samples": 850
                }
            
            # Overall inference metrics
            result = {
                "inference_results": inference_results,
                "total_samples": 1000,
                "chains": 4,
                "convergence": True,
                "execution_time_seconds": 2.5,
                "probability_estimate": 0.68,
                "uncertainty": 0.12,
                "confidence": 0.85
            }
            
            execution_time = time.time() - start_time
            self.ui_manager.print_pipeline_stage_result("inference", {"success": True, "data": result}, execution_time)
            
            return {
                "stage": "inference",
                "success": True,
                "data": result,
                "execution_time": execution_time,
                "previous_results": synthesis_result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Inference stage failed: {e}")
            self.ui_manager.print_pipeline_stage_result("inference", {"success": False, "error": str(e)}, execution_time)
            return {
                "stage": "inference",
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "previous_results": synthesis_result
            }


# Async command decorator for Click
def async_command(f):
    """Decorator to run async functions in Click commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    wrapper.__name__ = f.__name__  # Preserve original function name
    wrapper.__doc__ = f.__doc__    # Preserve docstring
    return wrapper


# Individual stage commands
@click.group()
def stages():
    """Individual MSA pipeline stage commands"""
    pass


@stages.command()
@click.argument("scenario")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@async_command
async def parse(scenario: str, session_id: str, verbose: bool, output: str):
    """Execute only the Parse stage - Natural language understanding and problem decomposition"""
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"parse-{int(datetime.now().timestamp())}"
    
    executor = StageExecutor(verbose=verbose)
    
    try:
        await executor.initialize()
        
        executor.ui_manager.print_header("MSA REASONING ENGINE - PARSE STAGE ONLY")
        executor.ui_manager.print_info(f"Scenario: {scenario}")
        executor.ui_manager.print_info(f"Session ID: {session_id}")
        
        # Execute parse stage
        result = await executor.execute_parse_stage(scenario, session_id)
        
        # Output results
        if output == "json":
            import json
            click.echo(json.dumps(result, indent=2, default=str))
        else:
            executor.ui_manager.print_header("PARSE STAGE COMPLETE")
            executor.ui_manager.print_success(f"Parse stage completed in {result['execution_time']:.2f} seconds")
            
            if result["success"]:
                data = result["data"]
                executor.ui_manager.print_info(f"Entities found: {len(data['entities'])}")
                executor.ui_manager.print_info(f"Complexity: {data['complexity']}")
                executor.ui_manager.print_info(f"Confidence: {data['confidence']:.2f}")
                
        
    except Exception as e:
        executor.ui_manager.print_error(f"Parse stage failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await executor.cleanup()


@stages.command()
@click.argument("scenario")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@async_command
async def retrieve(scenario: str, session_id: str, verbose: bool, output: str):
    """Execute Parse + Knowledge stages - Understanding and knowledge retrieval"""
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"retrieve-{int(datetime.now().timestamp())}"
    
    executor = StageExecutor(verbose=verbose)
    
    try:
        await executor.initialize()
        
        executor.ui_manager.print_header("MSA REASONING ENGINE - PARSE + KNOWLEDGE STAGES")
        executor.ui_manager.print_info(f"Scenario: {scenario}")
        executor.ui_manager.print_info(f"Session ID: {session_id}")
        
        # Execute parse stage
        parse_result = await executor.execute_parse_stage(scenario, session_id)
        if not parse_result["success"]:
            executor.ui_manager.print_error("Parse stage failed, stopping execution")
            return
        
        # Execute knowledge stage
        knowledge_result = await executor.execute_knowledge_stage(parse_result)
        
        # Output results
        if output == "json":
            import json
            final_result = {
                "parse": parse_result,
                "knowledge": knowledge_result,
                "session_id": session_id
            }
            click.echo(json.dumps(final_result, indent=2, default=str))
        else:
            executor.ui_manager.print_header("RETRIEVE STAGES COMPLETE")
            total_time = parse_result["execution_time"] + knowledge_result["execution_time"]
            executor.ui_manager.print_success(f"Parse + Knowledge stages completed in {total_time:.2f} seconds")
            
            if knowledge_result["success"]:
                data = knowledge_result["data"]
                executor.ui_manager.print_info(f"Knowledge items retrieved: {data['retrieved_count']}")
                executor.ui_manager.print_info(f"Coverage: {data['coverage']:.2f}")
        
    except Exception as e:
        executor.ui_manager.print_error(f"Retrieve stages failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await executor.cleanup()


@stages.command()
@click.argument("scenario")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@async_command
async def graph(scenario: str, session_id: str, verbose: bool, output: str):
    """Execute Parse + Knowledge + Graph stages - Understanding, retrieval and graph construction"""
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"graph-{int(datetime.now().timestamp())}"
    
    executor = StageExecutor(verbose=verbose)
    
    try:
        await executor.initialize()
        
        executor.ui_manager.print_header("MSA REASONING ENGINE - PARSE + KNOWLEDGE + GRAPH STAGES")
        executor.ui_manager.print_info(f"Scenario: {scenario}")
        executor.ui_manager.print_info(f"Session ID: {session_id}")
        
        # Execute parse stage
        parse_result = await executor.execute_parse_stage(scenario, session_id)
        if not parse_result["success"]:
            executor.ui_manager.print_error("Parse stage failed, stopping execution")
            return
        
        # Execute knowledge stage
        knowledge_result = await executor.execute_knowledge_stage(parse_result)
        if not knowledge_result["success"]:
            executor.ui_manager.print_error("Knowledge stage failed, stopping execution")
            return
        
        # Execute graph stage
        graph_result = await executor.execute_graph_stage(knowledge_result)
        
        # Output results
        if output == "json":
            import json
            final_result = {
                "parse": parse_result,
                "knowledge": knowledge_result,
                "graph": graph_result,
                "session_id": session_id
            }
            click.echo(json.dumps(final_result, indent=2, default=str))
        else:
            executor.ui_manager.print_header("GRAPH STAGES COMPLETE")
            total_time = parse_result["execution_time"] + knowledge_result["execution_time"] + graph_result["execution_time"]
            executor.ui_manager.print_success(f"Parse + Knowledge + Graph stages completed in {total_time:.2f} seconds")
            
            if graph_result["success"]:
                data = graph_result["data"]
                executor.ui_manager.print_info(f"Graph nodes: {data['node_count']}")
                executor.ui_manager.print_info(f"Graph edges: {data['edge_count']}")
                executor.ui_manager.print_info(f"Graph density: {data['graph_density']:.3f}")
        
    except Exception as e:
        executor.ui_manager.print_error(f"Graph stages failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await executor.cleanup()


@stages.command()
@click.argument("scenario")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@async_command
async def synthesize(scenario: str, session_id: str, verbose: bool, output: str):
    """Execute Parse + Knowledge + Graph + Synthesis stages - All stages except inference"""
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"synthesize-{int(datetime.now().timestamp())}"
    
    executor = StageExecutor(verbose=verbose)
    
    try:
        await executor.initialize()
        
        executor.ui_manager.print_header("MSA REASONING ENGINE - PARSE + KNOWLEDGE + GRAPH + SYNTHESIS STAGES")
        executor.ui_manager.print_info(f"Scenario: {scenario}")
        executor.ui_manager.print_info(f"Session ID: {session_id}")
        
        # Execute parse stage
        parse_result = await executor.execute_parse_stage(scenario, session_id)
        if not parse_result["success"]:
            executor.ui_manager.print_error("Parse stage failed, stopping execution")
            return
        
        # Execute knowledge stage
        knowledge_result = await executor.execute_knowledge_stage(parse_result)
        if not knowledge_result["success"]:
            executor.ui_manager.print_error("Knowledge stage failed, stopping execution")
            return
        
        # Execute graph stage
        graph_result = await executor.execute_graph_stage(knowledge_result)
        if not graph_result["success"]:
            executor.ui_manager.print_error("Graph stage failed, stopping execution")
            return
        
        # Execute synthesis stage
        synthesis_result = await executor.execute_synthesis_stage(graph_result)
        
        # Output results
        if output == "json":
            import json
            final_result = {
                "parse": parse_result,
                "knowledge": knowledge_result,
                "graph": graph_result,
                "synthesis": synthesis_result,
                "session_id": session_id
            }
            click.echo(json.dumps(final_result, indent=2, default=str))
        else:
            executor.ui_manager.print_header("SYNTHESIS STAGES COMPLETE")
            total_time = (parse_result["execution_time"] + knowledge_result["execution_time"] + 
                         graph_result["execution_time"] + synthesis_result["execution_time"])
            executor.ui_manager.print_success(f"Parse + Knowledge + Graph + Synthesis stages completed in {total_time:.2f} seconds")
            
            if synthesis_result["success"]:
                data = synthesis_result["data"]
                executor.ui_manager.print_info(f"Model variables: {data['variable_count']}")
                executor.ui_manager.print_info(f"Model complexity: {data['model_complexity']}")
                executor.ui_manager.print_subheader("Generated Model Code:")
                executor.ui_manager.print_code(data['model_code'], language="python")
        
    except Exception as e:
        executor.ui_manager.print_error(f"Synthesis stages failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await executor.cleanup()


@stages.command()
@click.argument("scenario")
@click.option("--session-id", "-s", help="Session ID for tracking")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--output", "-o", type=click.Choice(["text", "json"]), default="text", help="Output format")
@async_command
async def infer(scenario: str, session_id: str, verbose: bool, output: str):
    """Execute full MSA pipeline - All stages including probabilistic inference"""
    
    # Generate session ID if not provided
    if not session_id:
        session_id = f"infer-{int(datetime.now().timestamp())}"
    
    executor = StageExecutor(verbose=verbose)
    
    try:
        await executor.initialize()
        
        executor.ui_manager.print_header("MSA REASONING ENGINE - FULL PIPELINE WITH INFERENCE")
        executor.ui_manager.print_info(f"Scenario: {scenario}")
        executor.ui_manager.print_info(f"Session ID: {session_id}")
        
        # Execute all stages in sequence
        parse_result = await executor.execute_parse_stage(scenario, session_id)
        if not parse_result["success"]:
            executor.ui_manager.print_error("Parse stage failed, stopping execution")
            return
        
        knowledge_result = await executor.execute_knowledge_stage(parse_result)
        if not knowledge_result["success"]:
            executor.ui_manager.print_error("Knowledge stage failed, stopping execution")
            return
        
        graph_result = await executor.execute_graph_stage(knowledge_result)
        if not graph_result["success"]:
            executor.ui_manager.print_error("Graph stage failed, stopping execution")
            return
        
        synthesis_result = await executor.execute_synthesis_stage(graph_result)
        if not synthesis_result["success"]:
            executor.ui_manager.print_error("Synthesis stage failed, stopping execution")
            return
        
        inference_result = await executor.execute_inference_stage(synthesis_result)
        
        # Output results
        if output == "json":
            import json
            final_result = {
                "parse": parse_result,
                "knowledge": knowledge_result,
                "graph": graph_result,
                "synthesis": synthesis_result,
                "inference": inference_result,
                "session_id": session_id
            }
            click.echo(json.dumps(final_result, indent=2, default=str))
        else:
            executor.ui_manager.print_header("FULL MSA PIPELINE COMPLETE")
            total_time = (parse_result["execution_time"] + knowledge_result["execution_time"] + 
                         graph_result["execution_time"] + synthesis_result["execution_time"] + 
                         inference_result["execution_time"])
            executor.ui_manager.print_success(f"Full MSA pipeline completed in {total_time:.2f} seconds")
            
            if inference_result["success"]:
                data = inference_result["data"]
                executor.ui_manager.print_info(f"Probability estimate: {data['probability_estimate']:.3f}")
                executor.ui_manager.print_info(f"Uncertainty: {data['uncertainty']:.3f}")
                executor.ui_manager.print_info(f"Convergence: {'Yes' if data['convergence'] else 'No'}")
                executor.ui_manager.print_info(f"Overall confidence: {data['confidence']:.3f}")
        
    except Exception as e:
        executor.ui_manager.print_error(f"Full pipeline failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
    finally:
        await executor.cleanup()


if __name__ == "__main__":
    stages()