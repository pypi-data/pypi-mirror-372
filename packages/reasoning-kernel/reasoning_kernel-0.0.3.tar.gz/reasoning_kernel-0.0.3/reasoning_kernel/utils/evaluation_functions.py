"""
Evaluation Functions (Φ) for Model Synthesis Architecture

This module implements the evaluation functions used in the MSA pipeline
to score candidates at each stage, as described in the arXiv paper:
"Modeling Open-World Cognition as On-Demand Synthesis of Probabilistic Models"
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from semantic_kernel import Kernel

logger = logging.getLogger(__name__)


class EvaluationFunctions:
    """Evaluation functions for MSA pipeline stages"""
    
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
    
    async def evaluate_parse(
        self, 
        parse_candidates: List[Dict[str, Any]], 
        task: Dict[str, Any],
        k_parse: int = 3
    ) -> Tuple[List[float], Optional[Dict[str, Any]]]:
        """
        Φ_parse: Evaluate parse candidates for quality and coherence.
        
        Args:
            parse_candidates: List of candidate parses (Π_O, Π_Q)
            task: Original task τ = (B, O, Q)
            k_parse: Number of candidates to evaluate
            
        Returns:
            Tuple of scores and best candidate
        """
        scores = []
        best_candidate = None
        
        prompt_template = """
        Evaluate the quality of these natural language parses for probabilistic programming.
        
        Task: {task_description}
        
        Parse Candidates:
        {candidates_json}
        
        For each candidate, evaluate:
        1. Faithfulness to the original input
        2. Formal correctness as probabilistic program expressions
        3. Consistency with placeholder usage
        4. Overall coherence and usefulness for reasoning
        
        Return a JSON array of scores between 0.0 and 1.0 for each candidate, where 1.0 is perfect.
        Also return the index of the best candidate.
        
        Example response format:
        {{
            "scores": [0.8, 0.9, 0.7],
            "best_index": 1
        }}
        """
        
        try:
            # Prepare prompt
            task_description = json.dumps(task, indent=2)
            candidates_json = json.dumps(parse_candidates[:k_parse], indent=2)
            
            prompt = prompt_template.format(
                task_description=task_description,
                candidates_json=candidates_json
            )
            
            # Call LLM for evaluation
            response = await self.kernel.invoke(
                plugin_name="llm",
                function_name="generate_text",
                prompt=prompt
            )
            
            response_text = str(response).strip()
            
            # Parse response
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            evaluation_result = json.loads(response_text)
            scores = evaluation_result.get("scores", [0.5] * len(parse_candidates))
            best_index = evaluation_result.get("best_index", 0)
            
            if best_index < len(parse_candidates):
                best_candidate = parse_candidates[best_index]
            
            logger.info(
                f"Parse evaluation completed: {len(scores)} candidates scored"
            )
            return scores, best_candidate
            
        except Exception as e:
            logger.error(f"Parse evaluation failed: {e}")
            # Return default scores
            default_scores = [0.5] * len(parse_candidates)
            return default_scores, parse_candidates[0] if parse_candidates else None
    
    async def evaluate_relevance(
        self,
        b_aug_candidates: List[Dict[str, Any]],
        graph_candidates: List[Dict[str, Any]],
        parse_result: Dict[str, Any],
        task: Dict[str, Any],
        k_relevance: int = 3
    ) -> Tuple[List[float], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Φ_relevance: Evaluate relevance of background knowledge and conceptual graphs.
        
        Args:
            b_aug_candidates: List of augmented background knowledge candidates
            graph_candidates: List of conceptual dependency graph candidates
            parse_result: Best parse from previous stage
            task: Original task τ
            k_relevance: Number of candidate pairs to evaluate
            
        Returns:
            Tuple of scores, best B_aug, and best graph
        """
        scores = []
        best_b_aug = None
        best_graph = None
        
        prompt_template = """
        Evaluate the relevance and coherence of these background knowledge and conceptual graph pairs.
        
        Task: {task_description}
        Parse Result: {parse_result}
        
        Candidate Pairs:
        {candidates_json}
        
        For each candidate pair, evaluate:
        1. Relevance to the task and parse
        2. Completeness of variable descriptions
        3. Coherence of causal relationships in the graph
        4. Overall usefulness for model synthesis
        
        Return a JSON array of scores between 0.0 and 1.0 for each candidate pair, where 1.0 is perfect.
        Also return the index of the best pair.
        
        Example response format:
        {{
            "scores": [0.8, 0.9, 0.7],
            "best_index": 1
        }}
        """
        
        try:
            # Prepare candidate pairs
            candidate_pairs = []
            min_len = min(k_relevance, len(b_aug_candidates), len(graph_candidates))
            for i in range(min_len):
                candidate_pairs.append({
                    "b_aug": b_aug_candidates[i],
                    "graph": graph_candidates[i]
                })
            
            # Prepare prompt
            task_description = json.dumps(task, indent=2)
            parse_result_json = json.dumps(parse_result, indent=2)
            candidates_json = json.dumps(candidate_pairs, indent=2)
            
            prompt = prompt_template.format(
                task_description=task_description,
                parse_result=parse_result_json,
                candidates_json=candidates_json
            )
            
            # Call LLM for evaluation
            response = await self.kernel.invoke(
                plugin_name="llm",
                function_name="generate_text",
                prompt=prompt
            )
            
            response_text = str(response).strip()
            
            # Parse response
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            evaluation_result = json.loads(response_text)
            scores = evaluation_result.get("scores", [0.5] * len(candidate_pairs))
            best_index = evaluation_result.get("best_index", 0)
            
            if best_index < len(candidate_pairs):
                best_b_aug = b_aug_candidates[best_index]
                best_graph = graph_candidates[best_index]
            
            logger.info(
                f"Relevance evaluation completed: {len(scores)} candidate pairs scored"
            )
            return scores, best_b_aug, best_graph
            
        except Exception as e:
            logger.error(f"Relevance evaluation failed: {e}")
            # Return default scores
            min_len = min(len(b_aug_candidates), len(graph_candidates))
            default_scores = [0.5] * min_len
            best_b_aug = b_aug_candidates[0] if b_aug_candidates else None
            best_graph = graph_candidates[0] if graph_candidates else None
            return default_scores, best_b_aug, best_graph
    
    async def evaluate_model(
        self,
        program_candidates: List[str],
        k_program: int = 3
    ) -> Tuple[List[bool], Optional[str]]:
        """
        Φ_model: Evaluate probabilistic program candidates for executability.
        
        Args:
            program_candidates: List of probabilistic program code strings
            k_program: Number of candidates to evaluate
            
        Returns:
            Tuple of validity flags and best candidate
        """
        validity_flags = []
        best_candidate = None
        
        # Simple validity check - try to parse the code
        for i, program_code in enumerate(program_candidates[:k_program]):
            try:
                # Check for required NumPyro components
                has_numpyro = "numpyro" in program_code
                has_model_def = "def model" in program_code
                has_import = "import numpyro" in program_code
                
                if has_numpyro and has_model_def and has_import:
                    validity_flags.append(True)
                    if best_candidate is None:
                        best_candidate = program_code
                else:
                    validity_flags.append(False)
                    
            except Exception:
                validity_flags.append(False)
        
        # If no valid candidates, return the first one anyway for fallback
        if best_candidate is None and program_candidates:
            best_candidate = program_candidates[0]
            validity_flags = [False] * len(program_candidates)
        
        logger.info(
            f"Model evaluation completed: "
            f"{sum(validity_flags)}/{len(validity_flags)} valid programs"
        )
        return validity_flags, best_candidate


# Export the evaluation functions
__all__ = ["EvaluationFunctions"]