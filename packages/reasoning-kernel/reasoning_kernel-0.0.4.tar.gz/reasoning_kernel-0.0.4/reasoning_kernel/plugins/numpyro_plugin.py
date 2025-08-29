"""
NumPyro Reasoning Plugin for Semantic Kernel

Provides probabilistic reasoning capabilities through Semantic Kernel functions
using the NumPyro probabilistic programming framework. This plugin integrates
Bayesian inference, causal modeling, and uncertainty quantification into the
Semantic Kernel ecosystem.
"""

import json
import logging
from typing import Optional
import numpy as np

# Semantic Kernel imports
from semantic_kernel.functions import kernel_function

# Internal imports
from ..core.probabilistic_engine import (
    NumPyroEngine,
    get_numpyro_engine,
    InferenceMethod,
)

logger = logging.getLogger(__name__)


class NumPyroReasoningPlugin:
    """
    Semantic Kernel plugin for NumPyro probabilistic reasoning

    Provides kernel functions for:
    - Causal modeling and inference
    - Bayesian hypothesis testing
    - Uncertainty quantification
    - Probabilistic model synthesis
    - Predictive modeling with uncertainty
    """

    def __init__(self, engine: Optional[NumPyroEngine] = None, **engine_kwargs):
        """Initialize NumPyro reasoning plugin"""
        self._engine = engine or get_numpyro_engine(**engine_kwargs)
        logger.info("NumPyro Reasoning Plugin initialized")

    @kernel_function(
        description="Create a causal model from data to understand cause-effect relationships",
        name="create_causal_model"
    )
    async def create_causal_model(self, data_json: str, target_variable: str, method: str = "nuts") -> str:
        """
        Create a causal model to analyze cause-effect relationships

        Args:
            data_json: JSON string with variable data
            target_variable: Target variable name
            method: Inference method to use

        Returns:
            JSON string with causal relationships
        """
        try:
            # Parse input data
            data_dict = json.loads(data_json)

            # Convert to numpy arrays
            data = {}
            for var_name, values in data_dict.items():
                data[var_name] = np.array(values, dtype=np.float32)

            # Map method string to enum
            inference_method = InferenceMethod(method.lower())

            # Run causal inference
            relationships = await self._engine.infer_causal_relationships(
                data=data, target_variable=target_variable, method=inference_method
            )

            # Convert to serializable format
            result = {
                "causal_relationships": [
                    {
                        "cause": rel.cause,
                        "effect": rel.effect,
                        "strength": rel.strength,
                        "confidence": rel.confidence,
                        "type": rel.relation_type.value,
                        "evidence_available": bool(rel.evidence),
                    }
                    for rel in relationships
                ],
                "target_variable": target_variable,
                "inference_method": method,
                "num_relationships": len(relationships),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in create_causal_model: {e}")
            return json.dumps({"error": str(e), "function": "create_causal_model"})

    @kernel_function(
        description="Run Bayesian inference to estimate parameters and quantify uncertainty",
        name="run_bayesian_inference"
    )
    async def run_bayesian_inference(
        self, hypotheses_json: str, evidence_json: str, prior_knowledge_json: str = "{}"
    ) -> str:
        """
        Run Bayesian inference to synthesize probabilistic models

        Args:
            hypotheses_json: JSON array of hypothesis strings
            evidence_json: JSON object with evidence data
            prior_knowledge_json: JSON object with prior knowledge

        Returns:
            JSON string with inference results
        """
        try:
            # Parse inputs
            hypotheses = json.loads(hypotheses_json)
            evidence = json.loads(evidence_json)
            prior_knowledge = json.loads(prior_knowledge_json)

            # Run model synthesis
            result = await self._engine.synthesize_probabilistic_model(
                hypotheses=hypotheses, evidence=evidence, prior_knowledge=prior_knowledge
            )

            # Convert to serializable format
            output = {
                "summary_statistics": result.summary_stats,
                "diagnostics": result.diagnostics,
                "convergence_info": result.convergence_info,
                "num_hypotheses": len(hypotheses),
                "evidence_keys": list(evidence.keys()),
            }

            # Add sample statistics for key parameters
            if "hypothesis_weights" in result.summary_stats:
                weights_stats = result.summary_stats["hypothesis_weights"]
                output["hypothesis_analysis"] = {
                    "most_likely_hypothesis": int(np.argmax(weights_stats["mean"])),
                    "hypothesis_probabilities": weights_stats["mean"],
                    "uncertainty_levels": weights_stats["std"],
                }

            return json.dumps(output, indent=2)

        except Exception as e:
            logger.error(f"Error in run_bayesian_inference: {e}")
            return json.dumps({"error": str(e), "function": "run_bayesian_inference"})

    @kernel_function(
        description="Make predictions with uncertainty quantification using Bayesian methods",
        name="predict_with_uncertainty"
    )
    async def predict_with_uncertainty(
        self, model_description: str, input_data_json: str, query_variable: str, confidence_level: str = "0.95"
    ) -> str:
        """
        Make predictions with uncertainty quantification

        Args:
            model_description: Description of the predictive model
            input_data_json: Input data for prediction
            query_variable: Variable to predict
            confidence_level: Confidence level (0-1)

        Returns:
            JSON string with prediction and uncertainty
        """
        try:
            # Parse inputs
            input_data = json.loads(input_data_json)
            conf_level = float(confidence_level)

            # Create a simple predictive model based on description
            def predictive_model():
                """Dynamic predictive model"""
                from numpyro import sample
                import numpyro.distributions as dist

                # Simple linear model for demonstration
                alpha = sample("alpha", dist.Normal(0, 1))
                beta = sample("beta", dist.Normal(0, 1))
                sigma = sample("sigma", dist.HalfNormal(1))

                # Predicted value
                if "x" in input_data:
                    x_val = input_data["x"]
                    mean_pred = alpha + beta * x_val
                else:
                    mean_pred = alpha

                prediction = sample(query_variable, dist.Normal(mean_pred, sigma))

                return prediction

            # Run uncertainty quantification
            uncertainty_result = await self._engine.quantify_uncertainty(
                model_fn=predictive_model, data=input_data, query_variable=query_variable, confidence_level=conf_level
            )

            # Format results
            result = {
                "prediction": {
                    "mean": uncertainty_result.mean,
                    "std": uncertainty_result.std,
                    "credible_interval": {
                        "lower": uncertainty_result.credible_interval[0],
                        "upper": uncertainty_result.credible_interval[1],
                        "confidence_level": uncertainty_result.confidence_level,
                    },
                },
                "model_description": model_description,
                "query_variable": query_variable,
                "input_variables": list(input_data.keys()),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in predict_with_uncertainty: {e}")
            return json.dumps({"error": str(e), "function": "predict_with_uncertainty"})

    @kernel_function(
        description="Perform sensitivity analysis to understand how parameter changes affect outcomes",
        name="sensitivity_analysis"
    )
    async def sensitivity_analysis(
        self, base_data_json: str, parameters_to_vary: str, variation_range: str = "0.1"
    ) -> str:
        """
        Perform sensitivity analysis on model parameters

        Args:
            base_data_json: Baseline parameter values
            parameters_to_vary: Parameters to analyze
            variation_range: Range of variation (as fraction)

        Returns:
            JSON string with sensitivity analysis results
        """
        try:
            # Parse inputs
            base_data = json.loads(base_data_json)
            params_to_vary = json.loads(parameters_to_vary)
            var_range = float(variation_range)

            # Perform sensitivity analysis
            sensitivity_results = {}

            for param in params_to_vary:
                if param not in base_data:
                    continue

                base_value = base_data[param]
                param_sensitivities = []

                # Test variations around base value
                for factor in [1 - var_range, 1 + var_range]:
                    varied_data = base_data.copy()
                    varied_data[param] = base_value * factor

                    # Run quick inference with varied parameter
                    # This is a simplified sensitivity test
                    def sensitivity_model():
                        from numpyro import sample
                        import numpyro.distributions as dist

                        # Simple model to demonstrate sensitivity
                        effect = sample("effect", dist.Normal(varied_data.get(param, 0), 1))
                        return effect

                    # Get uncertainty for this variation
                    uncertainty = await self._engine.quantify_uncertainty(
                        model_fn=sensitivity_model, data=varied_data, query_variable="effect", confidence_level=0.95
                    )

                    param_sensitivities.append(
                        {
                            "variation_factor": factor,
                            "parameter_value": varied_data[param],
                            "effect_mean": uncertainty.mean,
                            "effect_std": uncertainty.std,
                        }
                    )

                # Calculate sensitivity metric
                if len(param_sensitivities) >= 2:
                    effect_change = abs(param_sensitivities[1]["effect_mean"] - param_sensitivities[0]["effect_mean"])
                    param_change = abs(
                        param_sensitivities[1]["parameter_value"] - param_sensitivities[0]["parameter_value"]
                    )

                    sensitivity_index = effect_change / param_change if param_change > 0 else 0

                    sensitivity_results[param] = {
                        "sensitivity_index": sensitivity_index,
                        "variations": param_sensitivities,
                        "base_value": base_value,
                    }

            # Rank parameters by sensitivity
            sorted_params = sorted(sensitivity_results.items(), key=lambda x: x[1]["sensitivity_index"], reverse=True)

            result = {
                "sensitivity_analysis": dict(sorted_params),
                "most_sensitive_parameter": (sorted_params[0][0] if sorted_params else None),
                "variation_range_tested": var_range,
                "parameters_analyzed": len(sensitivity_results),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in sensitivity_analysis: {e}")
            return json.dumps({"error": str(e), "function": "sensitivity_analysis"})

    @kernel_function(
        description="Test hypotheses using Bayesian hypothesis testing with Bayes factors",
        name="hypothesis_test"
    )
    async def hypothesis_test(
        self,
        null_hypothesis: str,
        alternative_hypothesis: str,
        observed_data_json: str,
        significance_level: str = "0.05",
    ) -> str:
        """
        Perform Bayesian hypothesis test

        Args:
            null_hypothesis: Null hypothesis description
            alternative_hypothesis: Alternative hypothesis description
            observed_data_json: Observed data
            significance_level: Significance level

        Returns:
            JSON string with hypothesis test results
        """
        try:
            # Parse inputs
            observed_data = json.loads(observed_data_json)
            alpha = float(significance_level)

            # Run hypothesis test
            test_result = await self._engine.run_hypothesis_test(
                null_hypothesis=null_hypothesis,
                alternative_hypothesis=alternative_hypothesis,
                data=observed_data,
                alpha=alpha,
            )

            # Add interpretation
            bayes_factor = test_result["bayes_factor"]

            if bayes_factor > 10:
                evidence_interpretation = "Strong evidence for null hypothesis"
            elif bayes_factor > 3:
                evidence_interpretation = "Moderate evidence for null hypothesis"
            elif bayes_factor > 1:
                evidence_interpretation = "Weak evidence for null hypothesis"
            elif bayes_factor > 0.33:
                evidence_interpretation = "Weak evidence for alternative"
            elif bayes_factor > 0.1:
                evidence_interpretation = "Moderate evidence for alternative"
            else:
                evidence_interpretation = "Strong evidence for alternative"

            result = {
                "hypothesis_test_results": test_result,
                "evidence_interpretation": evidence_interpretation,
                "null_hypothesis": null_hypothesis,
                "alternative_hypothesis": alternative_hypothesis,
                "decision": (
                    "Reject null hypothesis" if test_result["reject_null"] else "Fail to reject null hypothesis"
                ),
            }

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error in hypothesis_test: {e}")
            return json.dumps({"error": str(e), "function": "hypothesis_test"})

    @kernel_function(
        description="Get information about available NumPyro reasoning capabilities and methods",
        name="get_capabilities"
    )
    async def get_capabilities(self) -> str:
        """
        Get information about NumPyro reasoning capabilities

        Returns:
            JSON string with available capabilities
        """
        capabilities = {
            "probabilistic_reasoning": {
                "description": "Bayesian inference and probabilistic modeling",
                "methods": [
                    "MCMC sampling with NUTS",
                    "Variational inference",
                    "Model synthesis",
                    "Parameter estimation",
                ],
            },
            "causal_modeling": {
                "description": "Causal inference and relationship discovery",
                "methods": [
                    "Linear causal models",
                    "Causal effect estimation",
                    "Confounding detection",
                    "Mediation analysis",
                ],
            },
            "uncertainty_quantification": {
                "description": "Quantify uncertainty in predictions and estimates",
                "methods": [
                    "Credible intervals",
                    "Posterior distributions",
                    "Prediction intervals",
                    "Model uncertainty",
                ],
            },
            "hypothesis_testing": {
                "description": "Bayesian hypothesis testing",
                "methods": ["Bayes factor calculation", "Model comparison", "Evidence assessment", "Decision making"],
            },
            "sensitivity_analysis": {
                "description": "Analyze parameter sensitivity",
                "methods": [
                    "Parameter variation",
                    "Sensitivity indices",
                    "Robustness testing",
                    "Critical parameter identification",
                ],
            },
            "available_functions": [
                "create_causal_model",
                "run_bayesian_inference",
                "predict_with_uncertainty",
                "sensitivity_analysis",
                "hypothesis_test",
                "get_capabilities",
            ],
            "backend_info": {
                "engine": "NumPyro",
                "computation_backend": "JAX",
                "mock_mode": hasattr(self._engine, "_mock_mode"),
            },
        }

        return json.dumps(capabilities, indent=2)


# Plugin registration function
def create_numpyro_plugin(**kwargs) -> NumPyroReasoningPlugin:
    """Create and return NumPyro reasoning plugin instance"""
    return NumPyroReasoningPlugin(**kwargs)
