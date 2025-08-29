"""
NumPyro Daytona Semantic Kernel Plugin

Provides kernel functions that execute NumPyro models inside Daytona sandboxes.
This file calls into `DaytonaNumPyroExecutor` implemented in
`reasoning_kernel/services/daytona_numpyro_executor.py`.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

try:
    from semantic_kernel.functions import kernel_function
    from semantic_kernel.plugin_definition import kernel_plugin
    from semantic_kernel.kernel_pydantic import KernelBaseModel
except Exception:  # pragma: no cover - SK may not be installed
    # Define minimal decorators/classes so the module can be imported in tests
    def kernel_function(**kwargs):
        def _dec(f):
            return f

        return _dec

    def kernel_plugin(**kwargs):
        def _dec(cls):
            return cls

        return _dec

    class KernelBaseModel:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass


try:
    from reasoning_kernel.services.daytona_numpyro_executor import (
        get_daytona_numpyro_executor,
        NumPyroSandboxRequest,
    )
except Exception:
    get_daytona_numpyro_executor = None
    NumPyroSandboxRequest = None

logger = logging.getLogger(__name__)


@kernel_plugin(name="NumPyroDaytona", description="Execute NumPyro in Daytona sandbox")
class NumPyroDaytonaPlugin(KernelBaseModel):
    def __init__(self, executor=None):
        super().__init__()
        self._executor = executor or (get_daytona_numpyro_executor() if get_daytona_numpyro_executor else None)
        self._last_result = None

    @kernel_function(name="execute_in_sandbox", description="Execute arbitrary NumPyro model code in Daytona sandbox")
    async def execute_in_sandbox(
        self,
        model_code: str,
        model_type: str = "causal",
        data: Optional[str] = None,
        num_samples: int = 2000,
        num_warmup: int = 1000,
        num_chains: int = 2,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        if not self._executor:
            return {"status": "error", "error": "Daytona executor not available"}

        parsed_data = json.loads(data) if data else None

        req = NumPyroSandboxRequest(
            model_code=model_code,
            model_type=model_type,
            data=parsed_data,
            inference_params={
                "num_samples": num_samples,
                "num_warmup": num_warmup,
                "num_chains": num_chains,
            },
            timeout=timeout,
        )

        res = await self._executor.execute_model(req)
        self._last_result = res

        if res.status == "success":
            return {
                "status": "success",
                "posterior_stats": res.posterior_stats,
                "diagnostics": res.diagnostics,
                "execution_time": res.execution_time,
                "sandbox_id": res.sandbox_id,
            }
        return {"status": "error", "error": res.error}

    @kernel_function(name="create_causal_model_sandbox", description="Create and run a causal model in Daytona sandbox")
    async def create_causal_model_sandbox(
        self, variables: str, relationships: str, observations: Optional[str] = None
    ) -> Dict[str, Any]:
        # parse inputs
        var_list = [v.strip() for v in variables.split(",")] if variables else []
        rels = json.loads(relationships) if relationships else []
        obs = json.loads(observations) if observations else None

        # Generate a simple causal model code
        model_lines = [
            "def model(observations=None):",
            "    import numpyro",
            "    import numpyro.distributions as dist",
            "    import jax.numpy as jnp",
        ]

        for v in var_list:
            model_lines.append(f'    {v} = numpyro.sample("{v}", dist.Normal(0,1))')

        for rel in rels:
            p = rel.get("parent")
            c = rel.get("child")
            effect = rel.get("effect", 1.0)
            if p and c:
                model_lines.append(f"    {c}_effect = {p} * {effect}")
                model_lines.append(f'    {c} = numpyro.sample("{c}_caused", dist.Normal({c}_effect, 0.1))')

        model_lines.append("    if observations:")
        model_lines.append("        for var, val in observations.items():")
        model_lines.append("            numpyro.factor(f'obs_{var}', dist.Normal(locals()[var], 0.1).log_prob(val))")

        model_code = "\n".join(model_lines)

        # Use executor
        if not self._executor:
            return {"status": "error", "error": "Executor unavailable"}

        req = NumPyroSandboxRequest(model_code=model_code, data=obs)
        res = await self._executor.execute_model(req)

        if res.status == "success":
            return {"status": "success", "posterior_stats": res.posterior_stats, "diagnostics": res.diagnostics}
        return {"status": "error", "error": res.error}

    @kernel_function(name="run_hierarchical_model", description="Run a hierarchical model in Daytona sandbox")
    async def run_hierarchical_model(
        self, groups: str, observations_per_group: int = 10, prior_mean: float = 0.0, prior_std: float = 1.0
    ) -> Dict[str, Any]:
        group_list = [g.strip() for g in groups.split(",")] if groups else []

        model_code = f"""
def model(observations=None):
    import numpyro
    import numpyro.distributions as dist
    import jax.numpy as jnp

    n_groups = {len(group_list)}
    n_obs = {observations_per_group}

    mu_global = numpyro.sample('mu_global', dist.Normal({prior_mean}, {prior_std}))
    sigma_global = numpyro.sample('sigma_global', dist.HalfCauchy(1.0))

    with numpyro.plate('groups', n_groups):
        group_effects = numpyro.sample('group_effects', dist.Normal(mu_global, sigma_global))

    with numpyro.plate('obs', n_groups * n_obs):
        group_idx = jnp.repeat(jnp.arange(n_groups), n_obs)
        y = numpyro.sample('y', dist.Normal(group_effects[group_idx], 1.0))

    return y
"""

        req = NumPyroSandboxRequest(
            model_code=model_code, inference_params={"num_samples": 1500, "num_warmup": 750, "num_chains": 2}
        )
        res = await self._executor.execute_model(req)

        if res.status == "success":
            convergence = self._check_convergence(res.diagnostics)
            return {
                "status": "success",
                "groups": group_list,
                "posterior_stats": res.posterior_stats,
                "diagnostics": res.diagnostics,
                "convergence": convergence,
            }
        return {"status": "error", "error": res.error}

    def _check_convergence(self, diagnostics: Optional[Dict[str, Any]]) -> str:
        if not diagnostics:
            return "unknown"
        r_hat = diagnostics.get("r_hat", {})
        if not r_hat:
            return "unknown"
        max_r = max(r_hat.values()) if r_hat else 1.0
        if max_r < 1.01:
            return "excellent"
        if max_r < 1.05:
            return "good"
        if max_r < 1.1:
            return "moderate"
        return "poor"


def create_numpyro_daytona_plugin(**kwargs):
    return NumPyroDaytonaPlugin(**kwargs)
