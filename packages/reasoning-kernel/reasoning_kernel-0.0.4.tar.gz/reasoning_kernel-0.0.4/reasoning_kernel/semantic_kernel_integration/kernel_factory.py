"""
Semantic Kernel Factory for MSA Integration
===========================================

Factory for creating Semantic Kernel instances with MSA capabilities
using Azure OpenAI (gpt-5-mini, o4-mini, model-router, text-embedding-3-small),
Redis Cloud, and Daytona Cloud integration.

Implements the "Agent as a Step in a Process" pattern for the MSA pipeline.
"""

import os
import logging
from typing import Optional

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextEmbedding
from reasoning_kernel.config.settings import AzureOpenAIConfig, RedisConfig


logger = logging.getLogger(__name__)


class MSAKernelFactory:
    """Factory for creating SK kernels with MSA capabilities"""

    @staticmethod
    async def create_msa_kernel(
        azure_endpoint: Optional[str] = None,
        azure_api_key: Optional[str] = None,
        redis_url: Optional[str] = None,
        daytona_endpoint: Optional[str] = None,
    ) -> sk.Kernel:
        """
        Create a Semantic Kernel with full MSA pipeline capabilities

        Args:
            azure_endpoint: Azure OpenAI endpoint
            azure_api_key: Azure OpenAI API key
            redis_url: Redis Cloud connection string
            daytona_endpoint: Daytona Cloud endpoint

        Returns:
            Configured Semantic Kernel instance with MSA capabilities
        """
        logger.info("Creating MSA-enabled Semantic Kernel...")

        # Initialize kernel
        kernel = sk.Kernel()

        # Prefer centralized config (env-backed), allow explicit overrides
        cfg = AzureOpenAIConfig.from_env()
        endpoint = azure_endpoint or cfg.endpoint
        api_key = azure_api_key or cfg.api_key
        api_version = cfg.api_version

        if not endpoint or not api_key:
            raise ValueError("Azure OpenAI endpoint and API key are required")

        # Configure Azure OpenAI services using configured deployment names
        chat_gpt5_mini = AzureChatCompletion(
            deployment_name=cfg.gpt5_mini_deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        kernel.add_service(chat_gpt5_mini)

        chat_o4_mini = AzureChatCompletion(
            deployment_name=cfg.o4_mini_deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        kernel.add_service(chat_o4_mini)

        model_router = AzureChatCompletion(
            deployment_name=cfg.model_router_deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        kernel.add_service(model_router)

        embeddings = AzureTextEmbedding(
            deployment_name=cfg.text_embedding_small_deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )
        kernel.add_service(embeddings)

        logger.info("Azure OpenAI services configured successfully")

        # Configure memory with Redis Cloud (optional, modern SK patterns recommend vector stores and plugins)
        # Note: SemanticTextMemory is deprecated in modern SK; memory wiring is handled elsewhere (KernelManager).
        if redis_url or os.getenv("REDIS_URL"):
            try:
                import importlib

                redis_module = importlib.import_module("semantic_kernel.connectors.memory.redis")
                RedisMemoryStore = getattr(redis_module, "RedisMemoryStore")

                r_cfg = None
                try:
                    r_cfg = RedisConfig.from_env()
                except Exception:
                    r_cfg = None

                _ = RedisMemoryStore(
                    connection_string=redis_url or (r_cfg.connection_string if r_cfg else os.getenv("REDIS_URL")),
                    vector_size=(r_cfg.vector_size if r_cfg else 1536),
                    collection_name=(r_cfg.collection_name if r_cfg else "msa_knowledge"),
                )
                logger.info("Redis Cloud connection validated for vector store (registration handled elsewhere)")

            except ModuleNotFoundError:
                logger.warning("Redis connector not available; skipping Redis setup")
            except Exception as e:
                logger.warning(f"Redis configuration issue: {e}; proceeding without Redis")

        logger.info("MSA Kernel created successfully")
        return kernel

    @staticmethod
    async def create_development_kernel() -> sk.Kernel:
        """Create a simplified kernel for development and testing"""
        return await MSAKernelFactory.create_msa_kernel()


# Kernel singleton for global access
_kernel_instance: Optional[sk.Kernel] = None


async def get_msa_kernel(**kwargs) -> sk.Kernel:
    """Get or create the MSA kernel singleton"""
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = await MSAKernelFactory.create_msa_kernel(**kwargs)
    return _kernel_instance


def reset_kernel():
    """Reset the kernel singleton"""
    global _kernel_instance
    _kernel_instance = None
