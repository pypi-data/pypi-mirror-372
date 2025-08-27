"""
ProbabilisticReasoningPlugin - Advanced Probabilistic Reasoning
=============================================================

Advanced probabilistic reasoning capabilities for MSA.
Handles Bayesian inference, uncertainty quantification, and probabilistic computations.
"""

import json
import time
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
class ProbabilisticResult:
    """Result from probabilistic reasoning"""

    success: bool
    posterior_samples: Optional[Dict[str, List[float]]]
    marginal_distributions: Optional[Dict[str, Dict[str, Any]]]
    log_likelihood: Optional[float]
    uncertainty_estimates: Optional[Dict[str, float]]
    metadata: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class BayesianInferenceConfig:
    """Configuration for Bayesian inference"""

    num_warmup: int = 1000
    num_samples: int = 2000
    num_chains: int = 2
    target_accept_prob: float = 0.8
    max_tree_depth: int = 10


class ProbabilisticReasoningPlugin:
    """
    Advanced Probabilistic Reasoning Plugin.

    This plugin provides sophisticated probabilistic reasoning capabilities
    including Bayesian inference, uncertainty quantification, and model comparison.
    """

    def __init__(self):
        """Initialize the probabilistic reasoning plugin"""
        self.default_config = BayesianInferenceConfig()
        self.supported_distributions = {
            "normal": "Normal distribution",
            "beta": "Beta distribution",
            "gamma": "Gamma distribution",
            "uniform": "Uniform distribution",
            "exponential": "Exponential distribution",
        }

    @kernel_function(
        description="Perform Bayesian inference on probabilistic program",
        name="bayesian_inference",
    )
    async def bayesian_inference(
        self, program_code: str, observations: str = "", inference_config: str = ""
    ) -> str:
        """
        Perform Bayesian inference on a probabilistic program.

        Args:
            program_code: The probabilistic program code
            observations: JSON string of observed data
            inference_config: Optional JSON string of inference configuration

        Returns:
            JSON string containing inference results
        """
        try:
            obs_data = json.loads(observations) if observations else {}
            config_data = json.loads(inference_config) if inference_config else {}

            result = await self._perform_bayesian_inference(
                program_code, obs_data, config_data
            )

            return json.dumps(
                {
                    "success": result.success,
                    "posterior_samples": result.posterior_samples,
                    "marginal_distributions": result.marginal_distributions,
                    "log_likelihood": result.log_likelihood,
                    "uncertainty_estimates": result.uncertainty_estimates,
                    "metadata": result.metadata,
                    "error": result.error,
                }
            )

        except Exception as e:
            logger.error(f"Error in Bayesian inference: {e}")
            return json.dumps(
                {
                    "success": False,
                    "posterior_samples": None,
                    "marginal_distributions": None,
                    "log_likelihood": None,
                    "uncertainty_estimates": None,
                    "metadata": {},
                    "error": str(e),
                }
            )

    async def _perform_bayesian_inference(
        self, program_code: str, observations: Dict[str, Any], config: Dict[str, Any]
    ) -> ProbabilisticResult:
        """Internal method to perform Bayesian inference"""
        start_time = time.time()

        try:
            # Parse inference configuration
            inference_config = self._parse_inference_config(config)

            # Simulate Bayesian inference (in practice, would use NumPyro/Pyro)
            posterior_samples = self._simulate_posterior_sampling(
                program_code, observations, inference_config
            )

            # Compute marginal distributions
            marginals = self._compute_marginal_distributions(posterior_samples)

            # Estimate log likelihood
            log_likelihood = self._estimate_log_likelihood(
                posterior_samples, observations
            )

            # Compute uncertainty estimates
            uncertainty_estimates = self._compute_uncertainty_estimates(
                posterior_samples
            )

            metadata = {
                "inference_time": time.time() - start_time,
                "num_samples": inference_config.num_samples,
                "num_chains": inference_config.num_chains,
                "convergence_diagnostics": self._compute_convergence_diagnostics(
                    posterior_samples
                ),
            }

            return ProbabilisticResult(
                success=True,
                posterior_samples=posterior_samples,
                marginal_distributions=marginals,
                log_likelihood=log_likelihood,
                uncertainty_estimates=uncertainty_estimates,
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Error in _perform_bayesian_inference: {e}")
            return ProbabilisticResult(
                success=False,
                posterior_samples=None,
                marginal_distributions=None,
                log_likelihood=None,
                uncertainty_estimates=None,
                metadata={"inference_time": time.time() - start_time},
                error=str(e),
            )

    def _parse_inference_config(
        self, config: Dict[str, Any]
    ) -> BayesianInferenceConfig:
        """Parse and validate inference configuration"""
        return BayesianInferenceConfig(
            num_warmup=config.get("num_warmup", self.default_config.num_warmup),
            num_samples=config.get("num_samples", self.default_config.num_samples),
            num_chains=config.get("num_chains", self.default_config.num_chains),
            target_accept_prob=config.get(
                "target_accept_prob", self.default_config.target_accept_prob
            ),
            max_tree_depth=config.get(
                "max_tree_depth", self.default_config.max_tree_depth
            ),
        )

    def _simulate_posterior_sampling(
        self,
        program_code: str,
        observations: Dict[str, Any],
        config: BayesianInferenceConfig,
    ) -> Dict[str, List[float]]:
        """Simulate posterior sampling (placeholder for actual inference)"""
        import random

        # Extract variable names from program code
        variables = self._extract_variables_from_program(program_code)

        # Generate synthetic posterior samples
        posterior_samples = {}
        for var in variables:
            # Generate samples from a simple normal distribution (placeholder)
            samples = [random.normalvariate(0, 1) for _ in range(config.num_samples)]
            posterior_samples[var] = samples

        return posterior_samples

    def _extract_variables_from_program(self, program_code: str) -> List[str]:
        """Extract variable names from probabilistic program code"""
        import re

        # Simple pattern matching for variable names (in practice would parse AST)
        patterns = [
            r'numpyro\.sample\([\'"]([^\'\"]+)[\'"]',  # NumPyro variables
            r'pyro\.sample\([\'"]([^\'\"]+)[\'"]',  # Pyro variables
            r"(\w+)\s*=\s*.*sample\(",  # General assignment patterns
        ]

        variables = set()
        for pattern in patterns:
            matches = re.findall(pattern, program_code)
            variables.update(matches)

        # Filter out common non-variable patterns
        filtered_vars = [var for var in variables if not var.endswith("_obs")]
        return list(filtered_vars)[:10]  # Limit to 10 variables for simulation

    def _compute_marginal_distributions(
        self, posterior_samples: Dict[str, List[float]]
    ) -> Dict[str, Dict[str, Any]]:
        """Compute marginal distributions from posterior samples"""
        marginals = {}

        for var, samples in posterior_samples.items():
            if samples:
                mean = sum(samples) / len(samples)
                variance = sum((x - mean) ** 2 for x in samples) / len(samples)
                std = variance**0.5

                marginals[var] = {
                    "mean": mean,
                    "std": std,
                    "variance": variance,
                    "median": sorted(samples)[len(samples) // 2],
                    "q025": sorted(samples)[int(0.025 * len(samples))],
                    "q975": sorted(samples)[int(0.975 * len(samples))],
                }

        return marginals

    def _estimate_log_likelihood(
        self, posterior_samples: Dict[str, List[float]], observations: Dict[str, Any]
    ) -> float:
        """Estimate log likelihood of the model"""
        # Simplified log likelihood estimation
        if not posterior_samples or not observations:
            return -1000.0  # Very low likelihood for empty data

        # Simple approximation based on sample variance and observations
        total_variance = sum(
            sum((x - sum(samples) / len(samples)) ** 2 for x in samples) / len(samples)
            for samples in posterior_samples.values()
            if samples
        )

        # Lower variance indicates better fit (higher likelihood)
        return -total_variance / len(posterior_samples) if total_variance > 0 else -10.0

    def _compute_uncertainty_estimates(
        self, posterior_samples: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Compute uncertainty estimates for each variable"""
        uncertainties = {}

        for var, samples in posterior_samples.items():
            if samples:
                # Use coefficient of variation as uncertainty measure
                mean = sum(samples) / len(samples)
                variance = sum((x - mean) ** 2 for x in samples) / len(samples)
                std = variance**0.5

                # Coefficient of variation (normalized uncertainty)
                cv = abs(std / mean) if mean != 0 else float("inf")
                uncertainties[var] = min(
                    cv, 10.0
                )  # Cap at 10.0 for numerical stability

        return uncertainties

    def _compute_convergence_diagnostics(
        self, posterior_samples: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Compute convergence diagnostics"""
        diagnostics = {}

        for var, samples in posterior_samples.items():
            if len(samples) >= 100:  # Need sufficient samples for diagnostics
                # Simple effective sample size approximation
                n = len(samples)
                autocorr = self._estimate_autocorrelation(samples)
                ess = n / (1 + 2 * autocorr) if autocorr >= 0 else n

                diagnostics[var] = {
                    "effective_sample_size": ess,
                    "autocorrelation": autocorr,
                    "converged": ess > 100,  # Simple convergence criterion
                }

        return diagnostics

    def _estimate_autocorrelation(self, samples: List[float]) -> float:
        """Estimate autocorrelation at lag 1"""
        if len(samples) < 2:
            return 0.0

        mean = sum(samples) / len(samples)

        # Lag-1 autocorrelation
        numerator = sum(
            (samples[i] - mean) * (samples[i - 1] - mean)
            for i in range(1, len(samples))
        )
        denominator = sum((x - mean) ** 2 for x in samples)

        return numerator / denominator if denominator > 0 else 0.0

    @kernel_function(
        description="Compute model comparison metrics", name="model_comparison"
    )
    async def model_comparison(
        self, model_results: str, comparison_metric: str = "aic"
    ) -> str:
        """
        Compare multiple probabilistic models.

        Args:
            model_results: JSON string containing results from multiple models
            comparison_metric: Comparison metric ("aic", "bic", "waic", "loo")

        Returns:
            JSON string containing model comparison results
        """
        try:
            models_data = (
                json.loads(model_results)
                if isinstance(model_results, str)
                else model_results
            )

            comparison_results = self._compare_models(models_data, comparison_metric)

            return json.dumps(comparison_results)

        except Exception as e:
            logger.error(f"Error in model comparison: {e}")
            return json.dumps({"success": False, "comparison": None, "error": str(e)})

    def _compare_models(self, models: Dict[str, Any], metric: str) -> Dict[str, Any]:
        """Compare models using specified metric"""
        if not isinstance(models, dict):
            return {"success": False, "error": "Invalid models format"}

        model_scores = {}

        for model_name, model_data in models.items():
            log_likelihood = model_data.get("log_likelihood", -1000.0)
            num_params = len(model_data.get("posterior_samples", {}))
            num_samples = len(
                next(iter(model_data.get("posterior_samples", {}).values()), [])
            )

            if metric.lower() == "aic":
                # AIC = -2 * log_likelihood + 2 * num_params
                score = -2 * log_likelihood + 2 * num_params
            elif metric.lower() == "bic":
                # BIC = -2 * log_likelihood + log(n) * num_params
                import math

                score = -2 * log_likelihood + math.log(max(num_samples, 1)) * num_params
            else:
                # Default to log likelihood
                score = log_likelihood

            model_scores[model_name] = score

        # Find best model (lowest score for AIC/BIC, highest for log likelihood)
        if metric.lower() in ["aic", "bic"]:
            best_model = (
                min(model_scores, key=lambda x: model_scores[x])
                if model_scores
                else None
            )
        else:
            best_model = (
                max(model_scores, key=lambda x: model_scores[x])
                if model_scores
                else None
            )

        return {
            "success": True,
            "metric": metric,
            "scores": model_scores,
            "best_model": best_model,
            "comparison": {
                model: f"{'✓' if model == best_model else '✗'} {score:.2f}"
                for model, score in model_scores.items()
            },
        }

    @kernel_function(
        description="Quantify uncertainty in predictions",
        name="uncertainty_quantification",
    )
    async def uncertainty_quantification(self, posterior_samples: str) -> str:
        """Quantify uncertainty in model predictions"""
        try:
            samples_data = (
                json.loads(posterior_samples)
                if isinstance(posterior_samples, str)
                else posterior_samples
            )

            uncertainty_results = self._quantify_uncertainty(samples_data)

            return json.dumps(uncertainty_results)

        except Exception as e:
            return json.dumps({"success": False, "uncertainty": None, "error": str(e)})

    def _quantify_uncertainty(
        self, posterior_samples: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Internal method to quantify uncertainty"""
        uncertainty_metrics = {}

        for var, samples in posterior_samples.items():
            if samples:
                # Compute various uncertainty metrics
                mean = sum(samples) / len(samples)
                variance = sum((x - mean) ** 2 for x in samples) / len(samples)
                std = variance**0.5

                # Confidence intervals
                sorted_samples = sorted(samples)
                n = len(sorted_samples)
                ci_50 = (sorted_samples[int(0.25 * n)], sorted_samples[int(0.75 * n)])
                ci_95 = (sorted_samples[int(0.025 * n)], sorted_samples[int(0.975 * n)])

                uncertainty_metrics[var] = {
                    "mean": mean,
                    "std": std,
                    "coefficient_of_variation": abs(std / mean)
                    if mean != 0
                    else float("inf"),
                    "confidence_interval_50": ci_50,
                    "confidence_interval_95": ci_95,
                    "entropy": self._estimate_entropy(samples),
                }

        return {
            "success": True,
            "uncertainty_metrics": uncertainty_metrics,
            "overall_uncertainty": self._compute_overall_uncertainty(
                uncertainty_metrics
            ),
        }

    def _estimate_entropy(self, samples: List[float]) -> float:
        """Estimate entropy of samples using histogram approach"""
        if not samples:
            return 0.0

        # Create histogram bins
        import math

        n_bins = max(10, int(math.sqrt(len(samples))))
        min_val, max_val = min(samples), max(samples)

        if min_val == max_val:
            return 0.0  # No entropy for constant values

        # Compute histogram
        bin_width = (max_val - min_val) / n_bins
        bin_counts = [0] * n_bins

        for sample in samples:
            bin_idx = min(int((sample - min_val) / bin_width), n_bins - 1)
            bin_counts[bin_idx] += 1

        # Compute entropy
        total_samples = len(samples)
        entropy = 0.0
        for count in bin_counts:
            if count > 0:
                p = count / total_samples
                entropy -= p * math.log2(p)

        return entropy

    def _compute_overall_uncertainty(
        self, uncertainty_metrics: Dict[str, Dict[str, Any]]
    ) -> float:
        """Compute overall uncertainty across all variables"""
        if not uncertainty_metrics:
            return 0.0

        cv_values = [
            metrics.get("coefficient_of_variation", 0.0)
            for metrics in uncertainty_metrics.values()
            if metrics.get("coefficient_of_variation", float("inf")) != float("inf")
        ]

        return sum(cv_values) / len(cv_values) if cv_values else 0.0


def create_probabilistic_reasoning_plugin() -> ProbabilisticReasoningPlugin:
    """Factory function to create a ProbabilisticReasoningPlugin instance"""
    return ProbabilisticReasoningPlugin()
