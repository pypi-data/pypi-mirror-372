"""
MSA Semantic Kernel Integration Client
=====================================

Main client for interacting with the MSA system using Semantic Kernel.
Provides a unified interface for all MSA capabilities with your specific Azure setup.
"""

import logging
from typing import Dict, Any, Optional, List
from semantic_kernel.kernel import Kernel
from semantic_kernel.processes.kernel_process import KernelProcess
from semantic_kernel.functions.kernel_arguments import KernelArguments

from .kernel_factory import MSAKernelFactory
from ..config.settings import MSAConfig
from ..msa_plugins.understanding_plugin import UnderstandingPlugin
from ..msa_plugins.search_plugin import SearchPlugin
from ..msa_plugins.inference_plugin import InferencePlugin
from ..msa_plugins.synthesis_plugin import SynthesisPlugin
from ..msa_plugins.webppl_translator_plugin import WebPPLTranslatorPlugin
from ..msa_processes.msa_pipeline_process import MSAPipelineProcess


class MSAClient:
    """
    Main client for MSA Semantic Kernel integration.

    Provides a unified interface for:
    - MSA reasoning pipeline (4-stage process)
    - Individual plugin capabilities
    - Agent-based reasoning tasks
    - WebPPL program synthesis
    """

    def __init__(self, config: Optional[MSAConfig] = None):
        """
        Initialize MSA client with configuration.

        Args:
            config: MSAConfig instance. If None, will load from environment.
        """
        self._config = config or MSAConfig.from_env()
        self._kernel: Optional[Kernel] = None
        self._process: Optional[KernelProcess] = None
        self._logger = logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Initialize the MSA system with Semantic Kernel."""
        self._logger.info("Initializing MSA Semantic Kernel integration")

        # Create kernel with all services using correct method signature
        self._kernel = await MSAKernelFactory.create_msa_kernel(
            azure_endpoint=self._config.azure_config.endpoint,
            azure_api_key=self._config.azure_config.api_key,
            redis_url=self._config.redis_config.connection_string if self._config.redis_config else None,
            daytona_endpoint=self._config.daytona_config.endpoint if self._config.daytona_config else None,
        )

        # Register MSA plugins
        await self._register_plugins()

        # Initialize MSA process
        self._initialize_process()

        self._logger.info("MSA system initialized successfully")

    async def _register_plugins(self) -> None:
        """Register all MSA plugins with the kernel."""
        if not self._kernel:
            raise RuntimeError("Kernel not initialized")

        plugins = [
            (UnderstandingPlugin(), "understanding"),
            (SearchPlugin(), "search"),
            (InferencePlugin(), "inference"),
            (SynthesisPlugin(), "synthesis"),
            (WebPPLTranslatorPlugin(), "webppl"),
        ]

        for plugin, name in plugins:
            self._kernel.add_plugin(plugin, name)
            self._logger.info(f"Registered plugin: {name}")

    def _initialize_process(self) -> None:
        """Initialize the MSA pipeline process."""
        pipeline = MSAPipelineProcess()
        self._process = pipeline.create_process()
        self._logger.info("MSA pipeline process initialized")

    # Core MSA Pipeline Methods

    async def run_msa_pipeline(self, scenario: str) -> Dict[str, Any]:
        """
        Run the complete 4-stage MSA reasoning pipeline.

        Args:
            scenario: The scenario to reason about

        Returns:
            Dict containing results from all 4 stages
        """
        if not self._kernel or not self._process:
            raise RuntimeError("MSA system not initialized")

        self._logger.info(f"Running MSA pipeline for scenario: {scenario[:100]}...")

        # For now, run stages sequentially using plugins
        # This will be replaced with proper process execution once Process framework API is stable
        results = {}

        # Stage 1: Understanding
        results["understanding"] = await self.understand_scenario(scenario)

        # Stage 2: Search (use understanding as query)
        results["search"] = await self.search_knowledge(results["understanding"])

        # Stage 3: Inference (use search results and scenario)
        results["inference"] = await self.perform_inference([results["search"]], scenario)

        # Stage 4: Synthesis (combine all results)
        synthesis_input = f"Scenario: {scenario}\nUnderstanding: {results['understanding']}\nKnowledge: {results['search']}\nInference: {results['inference']}"
        results["synthesis"] = await self.synthesize_program(synthesis_input, [])

        self._logger.info("MSA pipeline execution completed")
        return results

    # Individual Plugin Methods

    async def understand_scenario(self, scenario: str) -> str:
        """
        Use the understanding plugin to parse and comprehend a scenario.

        Args:
            scenario: The scenario to understand

        Returns:
            Understanding analysis as string
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        function = self._kernel.get_function("understanding", "understand_scenario")
        arguments = KernelArguments(scenario=scenario)

        result = await self._kernel.invoke(function, arguments)
        return str(result)

    async def search_knowledge(self, query: str) -> str:
        """
        Search the knowledge base using semantic search.

        Args:
            query: Search query

        Returns:
            Search results as string
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        function = self._kernel.get_function("search", "search_knowledge")
        arguments = KernelArguments(query=query)

        result = await self._kernel.invoke(function, arguments)
        return str(result)

    async def perform_inference(self, premises: List[str], query: str) -> str:
        """
        Perform probabilistic inference using MSA reasoning.

        Args:
            premises: List of premise statements
            query: Query to infer

        Returns:
            Inference results as string
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        function = self._kernel.get_function("inference", "perform_inference")
        arguments = KernelArguments(premises=premises, query=query)

        result = await self._kernel.invoke(function, arguments)
        return str(result)

    async def synthesize_program(self, specification: str, examples: List[str]) -> str:
        """
        Synthesize a probabilistic program from specification and examples.

        Args:
            specification: Program specification
            examples: List of example inputs/outputs

        Returns:
            Synthesized program as string
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        function = self._kernel.get_function("synthesis", "synthesize_program")
        arguments = KernelArguments(specification=specification, examples=examples)

        result = await self._kernel.invoke(function, arguments)
        return str(result)

    async def translate_to_webppl(self, program_description: str) -> str:
        """
        Translate a program description to WebPPL code.

        Args:
            program_description: Description of the program to translate

        Returns:
            WebPPL code as string
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        function = self._kernel.get_function("webppl", "translate_to_webppl")
        arguments = KernelArguments(description=program_description)

        result = await self._kernel.invoke(function, arguments)
        return str(result)

    # Agent-based Methods

    async def run_reasoning_agent(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a reasoning agent for complex multi-step tasks.

        Args:
            task: The reasoning task
            context: Additional context for the task

        Returns:
            Agent reasoning results
        """
        if not self._kernel:
            raise RuntimeError("MSA system not initialized")

        # This would involve creating an agent and running it
        # For now, we'll use the pipeline approach
        return await self.run_msa_pipeline(f"Task: {task}\nContext: {context}")

    # Utility Methods

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get status information about the MSA system.

        Returns:
            System status dictionary
        """
        if not self._kernel:
            return {"status": "not_initialized"}

        services = []
        for service_id in self._kernel.services.keys():
            services.append(service_id)

        plugins = []
        for plugin_name, plugin in self._kernel.plugins.items():
            functions = []
            try:
                # Try to get function names from the plugin
                for func_name in plugin:
                    functions.append(func_name.name)
            except Exception:
                functions.append("unknown")
            plugins.append({"name": plugin_name, "functions": functions})

        return {
            "status": "initialized",
            "services": services,
            "plugins": plugins,
            "process_initialized": self._process is not None,
            "config": {
                "max_pipeline_steps": self._config.max_pipeline_steps,
                "confidence_threshold": self._config.confidence_threshold,
                "caching_enabled": self._config.enable_caching,
            },
        }

    async def close(self) -> None:
        """Clean up resources."""
        self._logger.info("Closing MSA client")
        # Add any cleanup logic here if needed


# Example usage and factory functions


async def create_msa_client(config: Optional[MSAConfig] = None) -> MSAClient:
    """
    Create and initialize an MSA client.

    Args:
        config: Optional MSAConfig. If None, loads from environment.

    Returns:
        Initialized MSA client
    """
    client = MSAClient(config)
    await client.initialize()
    return client


# For backwards compatibility with existing code
async def get_msa_client() -> MSAClient:
    """Get an initialized MSA client using environment configuration."""
    return await create_msa_client()


# Context manager support
class MSAClientContext:
    """Context manager for MSA client."""

    def __init__(self, config: Optional[MSAConfig] = None):
        self.config = config
        self.client: Optional[MSAClient] = None

    async def __aenter__(self) -> MSAClient:
        self.client = await create_msa_client(self.config)
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.client:
            await self.client.close()


# Convenience function for context manager usage
def msa_client(config: Optional[MSAConfig] = None) -> MSAClientContext:
    """
    Create an MSA client context manager.

    Usage:
        async with msa_client() as client:
            result = await client.run_msa_pipeline("Some scenario")
    """
    return MSAClientContext(config)
