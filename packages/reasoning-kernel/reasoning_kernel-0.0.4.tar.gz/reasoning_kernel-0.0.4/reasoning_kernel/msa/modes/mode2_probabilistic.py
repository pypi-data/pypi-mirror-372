"""
Mode 2: Dynamic probabilistic model synthesis using NumPyro
This mode acts as the "logical planner" building custom models for inference
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Any, Dict, List

import jax
import jax.numpy as jnp
import numpy as np
import numpyro
import numpyro.distributions as dist
from numpyro.handlers import seed
from numpyro.infer import MCMC
from numpyro.infer import NUTS
from numpyro.infer import Predictive
from reasoning_kernel.core.config_manager import get_config


logger = logging.getLogger(__name__)


class ProbabilisticModelSynthesizer:
    """Mode 2 of MSA - Dynamic probabilistic model synthesis"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.models_cache = {}

    async def synthesize_model(self, specifications: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize a probabilistic model based on specifications from Mode 1

        Args:
            specifications: Model specifications from knowledge extraction
            scenario_data: Additional data about the scenario

        Returns:
            Synthesized model results and inferences
        """
        try:
            logger.info("Synthesizing probabilistic model...")

            # Extract model components
            variables = specifications.get("variables", [])
            dependencies = specifications.get("dependencies", [])
            uncertainties = specifications.get("uncertainties", [])
            model_type = specifications.get("model_type", "generic_bayesian")

            # Create model structure
            model_structure = await self._create_model_structure(variables, dependencies, uncertainties)

            # Generate synthetic model if no data provided
            if not scenario_data.get("observations"):
                scenario_data = await self._generate_scenario_data(model_structure)

            # Run inference
            inference_results = await self._run_inference(model_structure, scenario_data)

            # Generate predictions
            predictions = await self._generate_predictions(model_structure, inference_results, scenario_data)

            # Calculate uncertainty measures
            uncertainty_analysis = await self._analyze_uncertainty(inference_results, predictions)

            result = {
                "model_structure": model_structure,
                "inference_results": inference_results,
                "predictions": predictions,
                "uncertainty_analysis": uncertainty_analysis,
                "model_type": model_type,
                "success": True,
            }

            logger.info("Probabilistic model synthesis completed successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to synthesize probabilistic model: {e}")
            return {
                "error": str(e),
                "model_structure": {},
                "inference_results": {},
                "predictions": {},
                "uncertainty_analysis": {},
                "success": False,
            }

    async def _create_model_structure(
        self, variables: List[Dict], dependencies: List[Dict], uncertainties: List[Dict]
    ) -> Dict[str, Any]:
        """Create the structure of the probabilistic model"""

        def create_model():
            """NumPyro model definition"""
            var_samples = {}

            # Create variables based on specifications
            for var in variables:
                var_name = var.get("name", f"var_{len(var_samples)}")
                var_type = var.get("type", "continuous")

                if var_type == "continuous":
                    # Use normal distribution as default for continuous variables
                    var_samples[var_name] = numpyro.sample(var_name, dist.Normal(0.0, 1.0))
                elif var_type == "discrete":
                    # Use Poisson for discrete variables
                    var_samples[var_name] = numpyro.sample(var_name, dist.Poisson(2.0))
                elif var_type == "categorical":
                    # Use Beta distribution as a simpler alternative for categorical-like behavior
                    var_samples[var_name] = numpyro.sample(var_name, dist.Beta(1.0, 1.0))

            # Add dependencies between variables
            for dep in dependencies:
                parent = dep.get("parent")
                child = dep.get("child")

                if parent in var_samples and child and child not in var_samples:
                    # Create dependent variable
                    parent_val = var_samples[parent]
                    var_samples[child] = numpyro.sample(child, dist.Normal(parent_val * 0.5, 0.3))

            return var_samples

        # Run model structure creation in thread pool
        loop = asyncio.get_event_loop()
        model_structure = await loop.run_in_executor(
            self.executor,
            lambda: {
                "variables": variables,
                "dependencies": dependencies,
                "uncertainties": uncertainties,
                # Don't include the function object to avoid JSON serialization issues
                # "model_function": create_model,
            },
        )

        return model_structure

    async def _generate_scenario_data(self, model_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate synthetic data for the scenario when no observations are provided"""

        def generate_data():
            # Create model function locally since we don't store it anymore
            def model_fn():
                """NumPyro model definition"""
                var_samples = {}

                # Create variables based on specifications
                for var in model_structure.get("variables", []):
                    var_name = var.get("name", f"var_{len(var_samples)}")
                    var_type = var.get("type", "continuous")

                    if var_type == "continuous":
                        # Use normal distribution as default for continuous variables
                        var_samples[var_name] = numpyro.sample(var_name, dist.Normal(0.0, 1.0))
                    elif var_type == "discrete":
                        # Use Poisson for discrete variables
                        var_samples[var_name] = numpyro.sample(var_name, dist.Poisson(2.0))
                    elif var_type == "categorical":
                        # Use Beta distribution as a simpler alternative for categorical-like behavior
                        var_samples[var_name] = numpyro.sample(var_name, dist.Beta(1.0, 1.0))

                # Add dependencies between variables
                for dep in model_structure.get("dependencies", []):
                    parent = dep.get("parent")
                    child = dep.get("child")

                    if parent in var_samples and child and child not in var_samples:
                        # Create dependent variable
                        parent_val = var_samples[parent]
                        var_samples[child] = numpyro.sample(child, dist.Normal(parent_val * 0.5, 0.3))

                return var_samples

            # Generate prior samples
            rng_key = jax.random.PRNGKey(42)
            prior_samples = {}

            with seed(rng_seed=42):
                # Sample from prior
                trace = numpyro.handlers.trace(model_fn).get_trace()
                for name, site in trace.items():
                    if site["type"] == "sample":
                        prior_samples[name] = float(site["value"])

            return {"observations": prior_samples, "data_type": "synthetic_prior", "sample_size": 1}

        loop = asyncio.get_event_loop()
        scenario_data = await loop.run_in_executor(self.executor, generate_data)

        return scenario_data

    async def _run_inference(self, model_structure: Dict[str, Any], scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run Bayesian inference on the synthesized model"""

        def run_mcmc():
            # Create model function locally since we don't store it anymore
            def model_fn():
                """NumPyro model definition"""
                var_samples = {}

                # Create variables based on specifications
                for var in model_structure.get("variables", []):
                    var_name = var.get("name", f"var_{len(var_samples)}")
                    var_type = var.get("type", "continuous")

                    if var_type == "continuous":
                        # Use normal distribution as default for continuous variables
                        var_samples[var_name] = numpyro.sample(var_name, dist.Normal(0.0, 1.0))
                    elif var_type == "discrete":
                        # Use Poisson for discrete variables
                        var_samples[var_name] = numpyro.sample(var_name, dist.Poisson(2.0))
                    elif var_type == "categorical":
                        # Use Beta distribution as a simpler alternative for categorical-like behavior
                        var_samples[var_name] = numpyro.sample(var_name, dist.Beta(1.0, 1.0))

                # Add dependencies between variables
                for dep in model_structure.get("dependencies", []):
                    parent = dep.get("parent")
                    child = dep.get("child")

                    if parent in var_samples and child and child not in var_samples:
                        # Create dependent variable
                        parent_val = var_samples[parent]
                        var_samples[child] = numpyro.sample(child, dist.Normal(parent_val * 0.5, 0.3))

                return var_samples

            observations = scenario_data.get("observations", {})

            # Check if model has any sample sites by running a test trace
            try:
                rng_key = jax.random.PRNGKey(42)
                with seed(rng_seed=42):
                    test_trace = numpyro.handlers.trace(model_fn).get_trace()
                    sample_sites = [name for name, site in test_trace.items() if site["type"] == "sample"]

                    if not sample_sites:
                        # Model has no sample sites - return diagnostic info instead of crashing
                        logger.warning("Model has no sample sites for inference. Returning diagnostic information.")
                        return {
                            "posterior_samples": {},
                            "num_samples": 0,
                            "inference_method": "diagnostic",
                            "diagnostic": "Model has no sample sites - likely due to empty model specification from AI service",
                            "error": "no_sample_sites",
                        }

            except Exception as e:
                logger.warning(f"Could not analyze model structure: {e}")
                # Continue with inference attempt, but log the issue

            try:
                # Condition model on observations
                conditioned_model = numpyro.handlers.condition(model_fn, observations)

                # Set up MCMC
                config = get_config()
                nuts_kernel = NUTS(conditioned_model)
                mcmc = MCMC(nuts_kernel, num_warmup=500, num_samples=config.probabilistic_samples, num_chains=1)

                # Run inference
                rng_key = jax.random.PRNGKey(0)
                mcmc.run(rng_key)

                # Extract samples
                samples = mcmc.get_samples()

                # Convert to Python types for JSON serialization
                processed_samples = {}
                for key, value in samples.items():
                    if hasattr(value, "shape") and value.shape:
                        processed_samples[key] = {
                            "mean": float(jnp.mean(value)),
                            "std": float(jnp.std(value)),
                            "samples": value.tolist()[:100],  # Limit samples for response size
                        }
                    else:
                        processed_samples[key] = {"mean": float(value), "std": 0.0, "samples": [float(value)]}

                return {
                    "posterior_samples": processed_samples,
                    "num_samples": config.probabilistic_samples,
                    "inference_method": "NUTS",
                }

            except Exception as inference_error:
                logger.error(f"MCMC inference failed: {inference_error}")
                return {
                    "posterior_samples": {},
                    "num_samples": 0,
                    "inference_method": "failed",
                    "diagnostic": f"MCMC inference failed: {str(inference_error)}",
                    "error": "inference_failed",
                }

        loop = asyncio.get_event_loop()
        inference_results = await loop.run_in_executor(self.executor, run_mcmc)

        return inference_results

    async def _generate_predictions(
        self, model_structure: Dict[str, Any], inference_results: Dict[str, Any], scenario_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate predictions using the inferred model"""

        def make_predictions():
            # Check if inference results contain valid samples
            posterior_samples = inference_results.get("posterior_samples", {})

            no_samples = not posterior_samples or inference_results.get("error") == "no_sample_sites"
            if no_samples:
                logger.warning("No posterior samples available for prediction - " "returning diagnostic info")
                return {
                    "predictive_distributions": {},
                    "prediction_method": "diagnostic",
                    "diagnostic": "No posterior samples available",
                    "error": "no_samples_for_prediction",
                }

            try:
                # Create model function locally since we don't store it anymore
                def model_fn():
                    """NumPyro model definition"""
                    var_samples = {}

                    # Create variables based on specifications
                    for var in model_structure.get("variables", []):
                        var_name = var.get("name", f"var_{len(var_samples)}")
                        var_type = var.get("type", "continuous")

                        if var_type == "continuous":
                            # Use normal distribution as default for continuous variables
                            var_samples[var_name] = numpyro.sample(var_name, dist.Normal(0.0, 1.0))
                        elif var_type == "discrete":
                            # Use Poisson for discrete variables
                            var_samples[var_name] = numpyro.sample(var_name, dist.Poisson(2.0))
                        elif var_type == "categorical":
                            # Use Beta distribution as a simpler alternative for categorical-like behavior
                            var_samples[var_name] = numpyro.sample(var_name, dist.Beta(1.0, 1.0))

                    # Add dependencies between variables
                    for dep in model_structure.get("dependencies", []):
                        parent = dep.get("parent")
                        child = dep.get("child")

                        if parent in var_samples and child and child not in var_samples:
                            # Create dependent variable
                            parent_val = var_samples[parent]
                            var_samples[child] = numpyro.sample(child, dist.Normal(parent_val * 0.5, 0.3))

                    return var_samples

                # Convert back to JAX arrays for prediction
                jax_samples = {}
                for key, stats in posterior_samples.items():
                    if "samples" in stats:
                        # Use subset for prediction
                        jax_samples[key] = jnp.array(stats["samples"][:100])

                if not jax_samples:
                    logger.warning("No valid samples for prediction")
                    return {
                        "predictive_distributions": {},
                        "prediction_method": "diagnostic",
                        "diagnostic": "No valid samples found for prediction",
                        "error": "no_valid_samples",
                    }

                # Generate predictive samples
                predictive = Predictive(model_fn, jax_samples)
                rng_key = jax.random.PRNGKey(1)

                predictions = predictive(rng_key)

                # Process predictions
                processed_predictions = {}
                for key, value in predictions.items():
                    if hasattr(value, "shape") and value.shape:
                        processed_predictions[key] = {
                            "mean": float(jnp.mean(value)),
                            "std": float(jnp.std(value)),
                            "percentile_25": float(jnp.percentile(value, 25)),
                            "percentile_75": float(jnp.percentile(value, 75)),
                            "min": float(jnp.min(value)),
                            "max": float(jnp.max(value)),
                        }

                return {"predictive_distributions": processed_predictions, "prediction_method": "posterior_predictive"}

            except Exception as prediction_error:
                logger.error(f"Prediction generation failed: {prediction_error}")
                return {
                    "predictive_distributions": {},
                    "prediction_method": "failed",
                    "diagnostic": f"Prediction failed: {prediction_error}",
                    "error": "prediction_failed",
                }

        loop = asyncio.get_event_loop()
        predictions = await loop.run_in_executor(self.executor, make_predictions)

        return predictions

    async def _analyze_uncertainty(
        self, inference_results: Dict[str, Any], predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze uncertainty in the model and predictions"""

        def calculate_uncertainty():
            config = get_config()
            posterior_samples = inference_results.get("posterior_samples", {})
            predictive_dists = predictions.get("predictive_distributions", {})

            uncertainty_analysis = {
                "epistemic_uncertainty": {},
                "aleatory_uncertainty": {},
                "total_uncertainty": {},
                "confidence_intervals": {},
            }

            # Calculate epistemic uncertainty (parameter uncertainty)
            for var_name, stats in posterior_samples.items():
                std_dev = stats.get("std", 0.0)
                mean_val = stats.get("mean", 1.0)
                coeff_of_var = std_dev / abs(mean_val) if mean_val != 0 else float("inf")
                uncertainty_analysis["epistemic_uncertainty"][var_name] = {
                    "standard_deviation": std_dev,
                    "coefficient_of_variation": coeff_of_var,
                }

            # Calculate predictive uncertainty
            for var_name, stats in predictive_dists.items():
                pred_std = stats.get("std", 0.0)
                p25 = stats.get("percentile_25", 0)
                p75 = stats.get("percentile_75", 0)
                uncertainty_analysis["total_uncertainty"][var_name] = {
                    "predictive_std": pred_std,
                    "prediction_interval_50": [p25, p75],
                }

            # Overall uncertainty assessment
            epistemic_vals = uncertainty_analysis["epistemic_uncertainty"]
            std_devs = [v["standard_deviation"] for v in epistemic_vals.values()]
            avg_epistemic = np.mean(std_devs) if std_devs else 0.0

            uncertainty_analysis["overall_assessment"] = {
                "average_epistemic_uncertainty": float(avg_epistemic),
                "uncertainty_level": (
                    "high"
                    if avg_epistemic > config.uncertainty_threshold
                    else "moderate" if avg_epistemic > 0.3 else "low"
                ),
                "model_confidence": max(0.0, 1.0 - float(avg_epistemic)),
            }

            return uncertainty_analysis

        loop = asyncio.get_event_loop()
        uncertainty_analysis = await loop.run_in_executor(self.executor, calculate_uncertainty)

        return uncertainty_analysis

    async def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)
            logger.info("Probabilistic model synthesizer cleanup completed")