"""
NumPyro Probabilistic Engine

Core engine providing Bayesian inference, causal modeling, and uncertainty
quantification using NumPyro and JAX. This engine powers the reasoning kernel's
probabilistic capabilities and integrates with the Semantic Kernel plugin
system.
"""

import asyncio
import warnings
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np

try:
    import jax
    import jax.numpy as jnp
    from jax import random
    import numpyro
    import numpyro.distributions as dist
    from numpyro import sample, plate
    from numpyro.infer import MCMC, NUTS
    from numpyro.diagnostics import hpdi, effective_sample_size, split_gelman_rubin

    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    warnings.warn("JAX/NumPyro not available. " "Probabilistic engine will use mock implementations.")


class InferenceMethod(Enum):
    """Available inference methods"""

    MCMC = "mcmc"
    NUTS = "nuts"
    HMC = "hmc"
    SVI = "svi"


class CausalRelationType(Enum):
    """Types of causal relationships"""

    DIRECT = "direct"
    INDIRECT = "indirect"
    CONFOUNDED = "confounded"
    MEDIATING = "mediating"


@dataclass
class CausalRelationship:
    """Represents a causal relationship between variables"""

    cause: str
    effect: str
    strength: float
    confidence: float
    relation_type: CausalRelationType
    evidence: Dict[str, Any]


@dataclass
class UncertaintyQuantification:
    """Uncertainty quantification results"""

    mean: float
    std: float
    credible_interval: Tuple[float, float]
    confidence_level: float
    samples: Optional[np.ndarray] = None


@dataclass
class BayesianInferenceResult:
    """Results from Bayesian inference"""

    posterior_samples: Dict[str, np.ndarray]
    summary_stats: Dict[str, Dict[str, float]]
    diagnostics: Dict[str, float]
    model_evidence: Optional[float] = None
    convergence_info: Dict[str, Any] = None


class NumPyroEngine:
    """
    Core NumPyro probabilistic reasoning engine

    Provides Bayesian inference, causal modeling, and uncertainty
    quantification capabilities using JAX/NumPyro for high-performance
    probabilistic programming.
    """

    def __init__(
        self,
        random_seed: int = 42,
        backend: str = "cpu",
        num_chains: int = 4,
        num_warmup: int = 1000,
        num_samples: int = 2000,
    ):
        """Initialize the NumPyro engine"""
        if not JAX_AVAILABLE:
            self._init_mock_engine()
            return

        self.random_seed = random_seed
        self.backend = backend
        self.num_chains = num_chains
        self.num_warmup = num_warmup
        self.num_samples = num_samples

        # Configure JAX backend
        self._configure_jax_backend()

        # Initialize random key
        self.rng_key = random.PRNGKey(random_seed)

        # Cache for compiled models
        self._compiled_models = {}

    def _init_mock_engine(self):
        """Initialize mock engine when JAX/NumPyro not available"""
        self._mock_mode = True
        print("WARNING: Using mock NumPyro engine. " "Install JAX and NumPyro for full functionality.")

    def _configure_jax_backend(self):
        """Configure JAX backend based on platform"""
        try:
            if self.backend == "gpu" and jax.default_backend() != "gpu":
                # Try to configure GPU
                pass
            elif self.backend == "metal":
                # Metal backend for Apple Silicon
                pass
            # CPU is default
        except Exception as e:
            warnings.warn(f"Could not configure JAX backend {self.backend}: {e}")

    async def infer_causal_relationships(
        self,
        data: Dict[str, np.ndarray],
        target_variable: str,
        method: InferenceMethod = InferenceMethod.NUTS,
        **kwargs,
    ) -> List[CausalRelationship]:
        """Infer causal relationships using Bayesian causal inference"""
        if hasattr(self, "_mock_mode"):
            return await self._mock_causal_inference(data, target_variable)

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_causal_inference, data, target_variable, method, kwargs
        )

    def _run_causal_inference(
        self, data: Dict[str, np.ndarray], target_variable: str, method: InferenceMethod, kwargs: Dict[str, Any]
    ) -> List[CausalRelationship]:
        """Run causal inference (blocking version)"""

        def causal_model():
            """NumPyro causal model"""
            n_vars = len(data) - 1  # excluding target
            var_names = [k for k in data.keys() if k != target_variable]

            # Prior on causal coefficients
            with plate("variables", n_vars):
                beta = sample("beta", dist.Normal(0, 1))

            # Prior on noise
            sigma = sample("sigma", dist.HalfNormal(1))

            # Linear causal model
            X = jnp.array([data[var] for var in var_names]).T
            y = data[target_variable]

            mean = jnp.dot(X, beta)
            sample("obs", dist.Normal(mean, sigma), obs=y)

        # Run inference
        kernel = NUTS(causal_model)
        mcmc = MCMC(kernel, num_warmup=self.num_warmup, num_samples=self.num_samples, num_chains=self.num_chains)

        mcmc.run(self.rng_key)
        samples = mcmc.get_samples()

        # Extract causal relationships
        relationships = []
        var_names = [k for k in data.keys() if k != target_variable]

        for i, var_name in enumerate(var_names):
            beta_samples = samples["beta"][:, i]
            strength = float(jnp.mean(beta_samples))
            confidence = float(1.0 - jnp.mean(jnp.abs(beta_samples) < 0.1))

            # Determine relationship type based on strength and consistency
            if abs(strength) > 0.5:
                rel_type = CausalRelationType.DIRECT
            elif abs(strength) > 0.2:
                rel_type = CausalRelationType.INDIRECT
            else:
                rel_type = CausalRelationType.CONFOUNDED

            relationships.append(
                CausalRelationship(
                    cause=var_name,
                    effect=target_variable,
                    strength=strength,
                    confidence=confidence,
                    relation_type=rel_type,
                    evidence={"posterior_samples": beta_samples},
                )
            )

        return relationships

    async def quantify_uncertainty(
        self, model_fn: callable, data: Dict[str, Any], query_variable: str, confidence_level: float = 0.95, **kwargs
    ) -> UncertaintyQuantification:
        """Quantify uncertainty for a specific variable using Bayesian inference"""
        if hasattr(self, "_mock_mode"):
            return await self._mock_uncertainty_quantification(query_variable, confidence_level)

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_uncertainty_quantification, model_fn, data, query_variable, confidence_level, kwargs
        )

    def _run_uncertainty_quantification(
        self,
        model_fn: callable,
        data: Dict[str, Any],
        query_variable: str,
        confidence_level: float,
        kwargs: Dict[str, Any],
    ) -> UncertaintyQuantification:
        """Run uncertainty quantification (blocking version)"""

        # Run MCMC inference
        kernel = NUTS(model_fn)
        mcmc = MCMC(kernel, num_warmup=self.num_warmup, num_samples=self.num_samples, num_chains=self.num_chains)

        mcmc.run(self.rng_key, **data)
        samples = mcmc.get_samples()

        if query_variable not in samples:
            raise ValueError(f"Query variable '{query_variable}' not found in " f"posterior samples")

        variable_samples = samples[query_variable]

        # Calculate statistics
        mean = float(jnp.mean(variable_samples))
        std = float(jnp.std(variable_samples))

        # Credible interval
        credible_interval = tuple(float(x) for x in hpdi(variable_samples, prob=confidence_level))

        return UncertaintyQuantification(
            mean=mean,
            std=std,
            credible_interval=credible_interval,
            confidence_level=confidence_level,
            samples=np.array(variable_samples),
        )

    async def synthesize_probabilistic_model(
        self, hypotheses: List[str], evidence: Dict[str, Any], prior_knowledge: Optional[Dict[str, Any]] = None
    ) -> BayesianInferenceResult:
        """Synthesize a probabilistic model from hypotheses and evidence"""
        if hasattr(self, "_mock_mode"):
            return await self._mock_model_synthesis(hypotheses, evidence)

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_model_synthesis, hypotheses, evidence, prior_knowledge or {}
        )

    def _run_model_synthesis(
        self, hypotheses: List[str], evidence: Dict[str, Any], prior_knowledge: Dict[str, Any]
    ) -> BayesianInferenceResult:
        """Run probabilistic model synthesis (blocking version)"""

        def synthesized_model():
            """Dynamically synthesized NumPyro model"""
            n_hypotheses = len(hypotheses)

            # Prior on hypothesis weights
            with plate("hypotheses", n_hypotheses):
                weights = sample("hypothesis_weights", dist.Dirichlet(jnp.ones(n_hypotheses)))

            # Model likelihood based on evidence
            for key, value in evidence.items():
                if isinstance(value, (int, float)):
                    # Continuous evidence
                    likelihood_mean = jnp.sum(weights * jnp.arange(n_hypotheses))
                    sample(f"evidence_{key}", dist.Normal(likelihood_mean, 1), obs=value)
                elif isinstance(value, bool):
                    # Binary evidence
                    likelihood_prob = jnp.sum(weights * jnp.linspace(0.1, 0.9, n_hypotheses))
                    sample(f"evidence_{key}", dist.Bernoulli(likelihood_prob), obs=value)

        # Run inference
        kernel = NUTS(synthesized_model)
        mcmc = MCMC(kernel, num_warmup=self.num_warmup, num_samples=self.num_samples, num_chains=self.num_chains)

        mcmc.run(self.rng_key)
        samples = mcmc.get_samples()

        # Calculate summary statistics
        summary_stats = {}
        for param, param_samples in samples.items():
            summary_stats[param] = {
                "mean": float(jnp.mean(param_samples)),
                "std": float(jnp.std(param_samples)),
                "median": float(jnp.median(param_samples)),
            }

        # Diagnostics
        diagnostics = {}
        for param, param_samples in samples.items():
            if param_samples.ndim > 1:  # Multi-chain
                diagnostics[f"{param}_rhat"] = float(split_gelman_rubin(param_samples))
                diagnostics[f"{param}_ess"] = float(effective_sample_size(param_samples))

        return BayesianInferenceResult(
            posterior_samples=samples,
            summary_stats=summary_stats,
            diagnostics=diagnostics,
            convergence_info={"chains": self.num_chains, "samples_per_chain": self.num_samples},
        )

    async def run_hypothesis_test(
        self, null_hypothesis: str, alternative_hypothesis: str, data: Dict[str, Any], alpha: float = 0.05
    ) -> Dict[str, Any]:
        """Run Bayesian hypothesis test"""
        if hasattr(self, "_mock_mode"):
            return await self._mock_hypothesis_test(null_hypothesis, alternative_hypothesis, alpha)

        return await asyncio.get_event_loop().run_in_executor(
            None, self._run_hypothesis_test, null_hypothesis, alternative_hypothesis, data, alpha
        )

    def _run_hypothesis_test(
        self, null_hypothesis: str, alternative_hypothesis: str, data: Dict[str, Any], alpha: float
    ) -> Dict[str, Any]:
        """Run Bayesian hypothesis test (blocking version)"""

        def hypothesis_model():
            """Bayesian hypothesis testing model"""
            # Prior probability of hypotheses
            p_null = sample("p_null", dist.Beta(1, 1))

            # Model selection indicator
            model_indicator = sample("model", dist.Bernoulli(p_null))

            # Different data generating processes for each hypothesis
            if "observed_value" in data:
                obs_val = data["observed_value"]
                with numpyro.handlers.mask(mask=(model_indicator == 0)):
                    # Null hypothesis model
                    sample("obs_null", dist.Normal(0, 1), obs=obs_val)

                with numpyro.handlers.mask(mask=(model_indicator == 1)):
                    # Alternative hypothesis model
                    effect_size = sample("effect_size", dist.Normal(0, 2))
                    sample("obs_alt", dist.Normal(effect_size, 1), obs=obs_val)

        # Run inference
        kernel = NUTS(hypothesis_model)
        mcmc = MCMC(kernel, num_warmup=500, num_samples=1000, num_chains=2)
        mcmc.run(self.rng_key)
        samples = mcmc.get_samples()

        # Bayes factor calculation
        p_null_posterior = jnp.mean(samples["p_null"])
        bayes_factor = p_null_posterior / (1 - p_null_posterior)

        # Decision
        reject_null = bayes_factor < (alpha / (1 - alpha))

        evidence_strength = "strong" if (bayes_factor > 10 or bayes_factor < 0.1) else "moderate"

        return {
            "bayes_factor": float(bayes_factor),
            "posterior_null_prob": float(p_null_posterior),
            "reject_null": bool(reject_null),
            "significance_level": alpha,
            "evidence_strength": evidence_strength,
        }

    # Mock implementations for when JAX/NumPyro not available
    async def _mock_causal_inference(self, data, target_variable):
        """Mock causal inference"""
        relationships = []
        for var in data.keys():
            if var != target_variable:
                relationships.append(
                    CausalRelationship(
                        cause=var,
                        effect=target_variable,
                        strength=np.random.normal(0, 0.5),
                        confidence=np.random.uniform(0.5, 0.9),
                        relation_type=CausalRelationType.DIRECT,
                        evidence={"mock": True},
                    )
                )
        return relationships

    async def _mock_uncertainty_quantification(self, query_variable, confidence_level):
        """Mock uncertainty quantification"""
        mean = np.random.normal(0, 1)
        std = np.random.uniform(0.1, 2.0)
        interval_width = 2 * std
        return UncertaintyQuantification(
            mean=mean,
            std=std,
            credible_interval=(mean - interval_width / 2, mean + interval_width / 2),
            confidence_level=confidence_level,
            samples=np.random.normal(mean, std, 100),
        )

    async def _mock_model_synthesis(self, hypotheses, evidence):
        """Mock model synthesis"""
        n_hypotheses = len(hypotheses)
        samples = {"hypothesis_weights": np.random.dirichlet([1] * n_hypotheses, 1000)}

        summary_stats = {
            "hypothesis_weights": {
                "mean": np.mean(samples["hypothesis_weights"], axis=0).tolist(),
                "std": np.std(samples["hypothesis_weights"], axis=0).tolist(),
                "median": np.median(samples["hypothesis_weights"], axis=0).tolist(),
            }
        }

        return BayesianInferenceResult(
            posterior_samples=samples, summary_stats=summary_stats, diagnostics={"mock": True}
        )

    async def _mock_hypothesis_test(self, null_hypothesis, alternative_hypothesis, alpha):
        """Mock hypothesis test"""
        bayes_factor = np.random.uniform(0.1, 10.0)
        p_null = 1 / (1 + bayes_factor)

        return {
            "bayes_factor": bayes_factor,
            "posterior_null_prob": p_null,
            "reject_null": bayes_factor < (alpha / (1 - alpha)),
            "significance_level": alpha,
            "evidence_strength": "moderate",
        }


# Global instance for easy access
_engine_instance = None


def get_numpyro_engine(**kwargs) -> NumPyroEngine:
    """Get or create global NumPyro engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = NumPyroEngine(**kwargs)
    return _engine_instance
