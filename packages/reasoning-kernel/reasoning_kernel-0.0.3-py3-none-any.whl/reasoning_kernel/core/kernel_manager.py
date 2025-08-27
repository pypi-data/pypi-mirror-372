"""Kernel Manager for Semantic Kernel 1.35.3+.

Modernized to use current Semantic Kernel patterns:
- Uses InMemoryStore instead of deprecated VolatileMemoryStore
- Direct service registration with kernel.add_service()
- Removed deprecated SemanticTextMemory and TextMemoryPlugin
- Modern memory management through vector stores and embedding services
"""

import logging
from typing import Any, Dict, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.in_memory import InMemoryStore
from semantic_kernel.core_plugins import ConversationSummaryPlugin
from semantic_kernel.core_plugins import HttpPlugin
from semantic_kernel.core_plugins import MathPlugin
from semantic_kernel.core_plugins import TextPlugin
from semantic_kernel.core_plugins import TimePlugin
from semantic_kernel.core_plugins import WebSearchEnginePlugin
from semantic_kernel.core_plugins.wait_plugin import WaitPlugin
from semantic_kernel.prompt_template.prompt_template_config import (
    PromptTemplateConfig,
)

try:
    from semantic_kernel.connectors.ai.google.google_ai.google_ai_settings import GoogleAISettings
    from semantic_kernel.connectors.ai.google.google_ai.services.google_ai_chat_completion import GoogleAIChatCompletion
    from semantic_kernel.connectors.ai.google.google_ai.services.google_ai_text_embedding import GoogleAITextEmbedding
    HAS_GOOGLE_AI = True
except ImportError:
    HAS_GOOGLE_AI = False
    GoogleAIChatCompletion = None
    GoogleAITextEmbedding = None

from reasoning_kernel.monitoring.tracing import initialize_tracing, trace_operation
from reasoning_kernel.core.token_management import (
    TiktokenCounter,
    CostEstimator,
    TokenBudgetManager,
)


logger = logging.getLogger(__name__)


class KernelManager:
    """Manager for Semantic Kernel initialization and configuration."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the kernel manager.

        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._kernel: Optional[Kernel] = None
        self._services: Dict[str, Any] = {}
        self._token_counter = TiktokenCounter()
        self._cost_estimator = CostEstimator(
            pricing_info={
                "gpt-5mini": {
                    "prompt_tokens": 0.03,
                    "completion_tokens": 0.06,
                },
                "gemini-2.5-pro": {
                    "prompt_tokens": 0.007,
                    "completion_tokens": 0.021,
                },
            }
        )
        self._budget_manager = TokenBudgetManager(budget=1000000)  # Default budget

    @property
    def kernel(self) -> Optional[Kernel]:
        """Public accessor for the configured kernel instance.

        Returns:
            Optional[Kernel]: The current kernel instance if created.
        """
        return self._kernel

    async def initialize(self) -> None:
        """Async initializer to configure and create the kernel.

        This method aligns with callers that expect an awaitable initialize().
        It loads configuration from environment (if not already provided)
        and creates a new Kernel instance with registered services/plugins.
        """
        # Only (re)initialize if kernel not already created
        if self._kernel is None:
            try:
                # Initialize tracing
                initialize_tracing()

                # Load configuration from env if not explicitly set
                if not self._config:
                    self.configure_from_env()
                self.create_kernel()
                
                # Verify that critical services are registered
                self._verify_critical_services()
                
            except Exception as e:
                logger.error(f"Failed to initialize KernelManager: {e}")
                raise

    async def cleanup(self) -> None:
        """Async cleanup hook to release resources.

        Semantic Kernel does not require explicit close for the core Kernel
        object; we clear references to allow GC and future reinitialization.
        """
        try:
            self._kernel = None
            # TODO: add cleanup for any services that require it when added
            logger.info("KernelManager cleaned up")
        except Exception as e:
            logger.warning(f"KernelManager cleanup encountered an issue: {e}")

    @trace_operation(name="invoke_prompt")
    async def invoke_prompt(
        self,
        prompt: str,
        *,
        max_tokens: int | None = 512,
        temperature: float | None = 0.2,
        top_p: float | None = 0.95,
        stop_sequences: list[str] | None = None,
    ) -> str:
        """Invoke an LLM with a raw prompt and return the text output.

        This provides a stable facade expected by MSA components, delegating to
        Semantic Kernel's convenience API when available. If no AI service is
        configured, returns an empty string so JSON-parsing callers degrade
        gracefully to defaults.

        Args:
            prompt: The prompt text to send to the model.
            max_tokens: Optional token limit for the completion.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            stop_sequences: Optional list of stop sequences.

        Returns:
            The model's textual completion. Empty string when unavailable.
        """
        # Ensure kernel exists
        if self._kernel is None:
            await self.initialize()

        # If still no kernel or no chat service, fail soft
        if self._kernel is None or "chat_completion" not in self._services:
            logger.warning("invoke_prompt called without an AI service configured; " "returning empty result")
            return ""

        # Token and cost management
        prompt_tokens = self._token_counter.count_tokens(prompt)
        result_text = ""

        try:
            chat_service = self._services.get("chat_completion")
            if chat_service is None:
                return ""

            # Use the modern get_chat_message_content method
            from semantic_kernel.contents import ChatMessageContent, AuthorRole

            messages = [ChatMessageContent(role=AuthorRole.USER, content=prompt)]
            completion = await chat_service.get_chat_message_content(messages)
            result_text = str(getattr(completion, "content", completion))

            # Finalize token and cost management
            completion_tokens = self._token_counter.count_tokens(result_text)
            cost = self._cost_estimator.estimate_cost(
                model_name=self._config.get("openai_model_id", "gpt-4"),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            self._budget_manager.update_usage(prompt_tokens + completion_tokens)

            logger.info(
                "LLM invocation complete",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost,
                budget_usage=self._budget_manager.get_usage_percentage(),
            )

            return result_text

        except Exception as e:
            logger.error(f"Direct chat service invocation failed: {e}")
            return ""

    def create_kernel(self) -> Kernel:
        """Create and configure a new kernel instance.

        Returns:
            Configured Kernel instance
        """
        logger.info("Creating new Semantic Kernel instance")

        # Create kernel
        kernel = Kernel()

        # Register AI services
        self._register_ai_services(kernel)

        # Register memory services
        self._register_memory_services(kernel)

        # Register core plugins
        self._register_core_plugins(kernel)

        self._kernel = kernel
        logger.info("Kernel created and configured successfully")

        return kernel

    def _register_ai_services(self, kernel: Kernel) -> None:
        """Register AI services with the kernel."""
        service_map = {
            "google_ai": self._register_google_ai,
            "azure_openai": self._register_azure_openai,
            "openai": self._register_openai,
        }

        for service_name, register_func in service_map.items():
            if register_func(kernel):
                return

        logger.error("No AI service configuration found. Please check your environment variables.")

    def _register_google_ai(self, kernel: Kernel) -> bool:
        """Register Google AI services."""
        if HAS_GOOGLE_AI and self._config.get("google_ai_api_key"):
            try:
                if GoogleAIChatCompletion is not None:
                    service = GoogleAIChatCompletion(
                        model_id=self._config.get("google_ai_model_id", "gemini-1.5-pro"),
                        api_key=self._config.get("google_ai_api_key"),
                        service_id="chat_completion",
                    )
                    kernel.add_service(service)
                    self._services["chat_completion"] = service
                    logger.info("Registered Google AI chat completion service")
                    return True
            except Exception as e:
                logger.warning(f"Failed to register Google AI chat completion service: {e}")
        return False

    def _register_azure_openai(self, kernel: Kernel) -> bool:
        """Register Azure OpenAI services."""
        api_key = self._config.get("azure_api_key")
        endpoint = self._config.get("azure_endpoint")
        deployment_name = self._config.get("azure_deployment_name")

        if api_key and endpoint and deployment_name:
            service = AzureChatCompletion(
                deployment_name=deployment_name,
                endpoint=endpoint,
                api_key=api_key,
                api_version=self._config.get("azure_api_version", "2025-01-01-preview"),
                service_id="chat_completion",
            )
            kernel.add_service(service)
            self._services["chat_completion"] = service
            logger.info("Registered Azure OpenAI chat completion service")
            return True
        return False

    def _register_openai(self, kernel: Kernel) -> bool:
        """Register OpenAI services."""
        if self._config.get("openai_api_key"):
            service = OpenAIChatCompletion(
                ai_model_id=self._config.get("openai_model_id", "gpt-4"),
                api_key=self._config.get("openai_api_key"),
                org_id=self._config.get("openai_org_id"),
                service_id="chat_completion",
            )
            kernel.add_service(service)
            self._services["chat_completion"] = service
            logger.info("Registered OpenAI chat completion service")
            return True
        return False

    def _register_memory_services(self, kernel: Kernel) -> None:
        """Register memory services with the kernel.

        Args:
            kernel: Kernel instance
        """
        # Create modern in-memory vector store
        memory_store = InMemoryStore()

        # Create embeddings service (support Google AI, OpenAI and Azure OpenAI)
        embeddings_service = None
        if HAS_GOOGLE_AI and self._config.get("google_ai_api_key"):
            try:
                if GoogleAITextEmbedding is not None:
                    embeddings_service = GoogleAITextEmbedding(
                        service_id="embedding",
                        embedding_model_id=self._config.get(
                            "google_ai_embedding_model_id",
                            "models/embedding-001"
                        ),
                        api_key=self._config.get("google_ai_api_key"),
                    )
            except Exception as e:
                logger.warning(f"Failed to create Google AI embedding service: {e}")
        elif self._config.get("use_azure_openai") and self._config.get("azure_api_key"):
            embeddings_service = AzureTextEmbedding(
                service_id="embedding",
                deployment_name=self._config.get("azure_embedding_deployment_name", "text-embedding-3-large"),
                endpoint=self._config.get("azure_endpoint"),
                api_key=self._config.get("azure_api_key"),
                api_version=self._config.get("azure_api_version", "2024-02-15-preview"),
            )
        elif self._config.get("openai_api_key"):
            embeddings_service = OpenAITextEmbedding(
                service_id="embedding",
                ai_model_id=self._config.get("embedding_model_id", "text-embedding-3-large"),
                api_key=self._config.get("openai_api_key"),
                org_id=self._config.get("openai_org_id"),
            )

        # Register embedding service with kernel for modern usage pattern
        if embeddings_service:
            kernel.add_service(embeddings_service)

            # Store references for internal use
            self._services["memory_store"] = memory_store
            self._services["embeddings"] = embeddings_service
            logger.info("Registered modern in-memory store and embeddings services")
        else:
            logger.warning("No embedding service configuration found")

    def _register_core_plugins(self, kernel: Kernel) -> None:
        """Register core plugins with the kernel.

        Args:
            kernel: Kernel instance
        """
        # Register built-in plugins
        # Prepare minimal prompt template config for conversation summary
        conv_config = PromptTemplateConfig(
            name="conversation_summary", template="{{input}}", template_format="semantic-kernel"
        )
        plugins = {
            "conversation": ConversationSummaryPlugin(conv_config),
            "http": HttpPlugin(),
            "math": MathPlugin(),
            "text": TextPlugin(),
            "time": TimePlugin(),
            "wait": WaitPlugin(),
            # Note: TextMemoryPlugin is deprecated - modern memory management
            # is handled through vector stores and embedding services registered above
        }

        # Add web search if configured
        if self._config.get("bing_api_key"):
            plugins["web_search"] = WebSearchEnginePlugin(self._config.get("bing_api_key"))

        for plugin_name, plugin in plugins.items():
            kernel.add_plugin(plugin, plugin_name)
            logger.info(f"Registered plugin: {plugin_name}")

        logger.info("Core plugins registered with modern memory services")

        # Register reasoning kernel specific plugins
        self._register_reasoning_plugins(kernel)

    def _register_reasoning_plugins(self, kernel: Kernel) -> None:
        """Register reasoning kernel specific plugins.

        Args:
            kernel: Kernel instance
        """
        try:
            # Register basic plugins that don't have complex dependencies
            basic_plugins = self._register_basic_reasoning_plugins(kernel)

            # Register advanced plugins with dependencies (if all components are ready)
            self._register_advanced_reasoning_plugins(kernel, basic_plugins)

        except ImportError as e:
            logger.warning(f"Some reasoning plugins could not be imported: {e}")
        except Exception as e:
            logger.error(f"Failed to register reasoning plugins: {e}")
            # Don't re-raise here to allow kernel to continue with partial plugin registration
            # This ensures the CLI can still function even if some plugins are missing

    def _register_basic_reasoning_plugins(self, kernel: Kernel) -> dict:
        """Register basic reasoning plugins without complex dependencies."""
        plugins_registered = {}

        try:
            # Import and register basic plugins
            from ..plugins import (
                InferencePlugin,
            )
            from ..plugins.langextract_plugin import LangExtractPlugin

            from ..services.memory_service import MemoryService

            memory_service = MemoryService(
                self._services.get("memory_store"), self._services.get("embeddings")
            )
            self._services["memory_service"] = memory_service

            # These plugins have simple or no dependencies
            basic_plugins = {
                "inference": InferencePlugin(),  # Takes optional sandbox_config
                "langextract": LangExtractPlugin(),  # Takes optional config
            }

            for plugin_name, plugin in basic_plugins.items():
                kernel.add_plugin(plugin, plugin_name)
                plugins_registered[plugin_name] = plugin
                logger.info(f"Registered basic reasoning plugin: {plugin_name}")

        except Exception as e:
            logger.warning(f"Error registering basic plugins: {e}")

        return plugins_registered

    def _register_advanced_reasoning_plugins(self, kernel: Kernel, basic_plugins: dict) -> None:
        """Register advanced reasoning plugins that have dependencies."""
        try:
            # Import plugins that need kernel or other dependencies
            from ..plugins import KnowledgePlugin

            # Get Redis client if available
            redis_client = self._services.get("redis_client")

            # Register plugins that need kernel
            kernel_plugins = {}

            # Register knowledge plugin if redis is available
            if redis_client:
                kernel_plugins["knowledge"] = KnowledgePlugin(redis_client=redis_client)

            for plugin_name, plugin in kernel_plugins.items():
                kernel.add_plugin(plugin, plugin_name)
                logger.info(f"Registered advanced reasoning plugin: {plugin_name}")

            # Note: Complex plugins like ThinkingExplorationPlugin, SampleEfficientLearningPlugin,
            # and MSAThinkingIntegrationPlugin require hierarchical managers and multiple dependencies.
            # These will be registered separately when the full system is initialized.
            logger.info("Advanced reasoning plugins with kernel dependencies registered")

        except ImportError as e:
            logger.warning(f"Could not import advanced reasoning plugins: {e}")
        except Exception as e:
            logger.error(f"Error registering advanced plugins: {e}")
            # Re-raise to ensure initialization fails visibly if critical plugins can't be registered
            raise

    def get_kernel(self) -> Optional[Kernel]:
        """Get the current kernel instance.

        Returns:
            Kernel instance or None
        """
        return self._kernel

    def get_service(self, service_id: str) -> Optional[Any]:
        """Get a registered service by ID.

        Args:
            service_id: Service identifier

        Returns:
            Service instance or None
        """
        return self._services.get(service_id)

    def get_memory_collection(self, record_type: type, collection_name: Optional[str] = None):
        """Get a memory collection from the InMemoryStore.

        Args:
            record_type: The type of record to store in the collection
            collection_name: Optional collection name, defaults to record_type.__name__

        Returns:
            Collection instance or None if memory store not available
        """
        memory_store = self._services.get("memory_store")
        if memory_store:
            return memory_store.get_collection(record_type=record_type)
        else:
            logger.warning("Memory store not available - ensure kernel is created with proper configuration")
            return None

    def add_custom_plugin(self, kernel: Kernel, plugin: object, plugin_name: str) -> None:
        """Add a custom plugin to the kernel.

        Args:
            kernel: Kernel instance
            plugin: Plugin instance
            plugin_name: Name for the plugin
        """
        kernel.add_plugin(plugin, plugin_name)
        logger.info(f"Added custom plugin: {plugin_name}")

    def configure_from_env(self) -> None:
        """Configure the manager from environment variables."""
        import os

        from reasoning_kernel.core.env import load_project_dotenv

        load_project_dotenv()

        # OpenAI configuration
        self._config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
        self._config["openai_model_id"] = os.getenv("OPENAI_MODEL_ID", "gpt-4")
        self._config["openai_org_id"] = os.getenv("OPENAI_ORG_ID")
        self._config["embedding_model_id"] = os.getenv("EMBEDDING_MODEL_ID", "text-embedding-ada-002")

        # Azure OpenAI configuration - support both short and long variable names
        self._config["use_azure_openai"] = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
        
        # Try long names first (AZURE_OPENAI_*), fall back to short names (AZURE_*)
        self._config["azure_deployment_name"] = os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("AZURE_DEPLOYMENT_NAME")
        self._config["azure_endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("AZURE_ENDPOINT")
        self._config["azure_api_key"] = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_API_KEY")
        self._config["azure_api_version"] = os.getenv("AZURE_OPENAI_API_VERSION") or os.getenv("AZURE_API_VERSION", "2024-02-15-preview")
        
        # Also support embedding-specific variables
        self._config["azure_embedding_deployment_name"] = os.getenv("AZURE_EMBEDDING_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")

        # Other services
        self._config["bing_api_key"] = os.getenv("BING_API_KEY")

        # Google AI configuration - support multiple variable naming conventions
        self._config["google_ai_api_key"] = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self._config["google_ai_model_id"] = os.getenv("GOOGLE_AI_GEMINI_MODEL_ID") or os.getenv("GOOGLE_AI_MODEL_ID", "gemini-1.5-pro")
        self._config["google_ai_embedding_model_id"] = os.getenv("GEMINI_EMBEDDING_MODEL") or os.getenv(
            "GOOGLE_AI_EMBEDDING_MODEL_ID",
            "models/embedding-001"
        )

        logger.info("Configuration loaded from environment variables")
        
    def _verify_critical_services(self) -> None:
        """Verify that critical services are registered and log warnings for missing ones."""
        critical_services = ["chat_completion"]
        missing_services = []
        
        for service_id in critical_services:
            if service_id not in self._services:
                missing_services.append(service_id)
                
        if missing_services:
            logger.warning(f"Missing critical services: {missing_services}. Some functionality may be limited.")
        
        # Check if we have at least one AI service
        if "chat_completion" not in self._services:
            logger.error("No AI chat completion service registered. Please check your environment configuration.")
