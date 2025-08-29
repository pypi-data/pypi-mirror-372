"""
Configuration settings for MSA Semantic Kernel integration
=========================================================

Configuration classes for Azure OpenAI, Redis Cloud, and Daytona Cloud.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AzureOpenAIConfig:
    """Configuration for Azure OpenAI services"""

    endpoint: str
    api_key: str
    api_version: str = "2025-04-01-preview"

    # Deployment names for your specific models
    gpt5_mini_deployment: str = "gpt-5-mini"
    o4_mini_deployment: str = "o4-mini"
    model_router_deployment: str = "model-router"
    text_embedding_small_deployment: str = "text-embedding-3-small"

    @classmethod
    def from_env(cls) -> "AzureOpenAIConfig":
        """Create configuration from environment variables"""
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_key = os.getenv("AZURE_OPENAI_API_KEY")

        if not endpoint or not api_key:
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set")

        return cls(
            endpoint=endpoint,
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
            gpt5_mini_deployment=os.getenv("AZURE_OPENAI_GPT5_MINI_DEPLOYMENT", "gpt-5-mini"),
            o4_mini_deployment=os.getenv("AZURE_OPENAI_O4_MINI_DEPLOYMENT", "o4-mini"),
            model_router_deployment=os.getenv("AZURE_OPENAI_MODEL_ROUTER_DEPLOYMENT", "model-router"),
            # Support both legacy and new env var names for embeddings
            text_embedding_small_deployment=(
                os.getenv("AZURE_OPENAI_TEXT_EMBEDDING_DEPLOYMENT")
                or os.getenv("AZURE_OPENAI_TEXT_EMBEDDING_SMALL_DEPLOYMENT")
                or "text-embedding-3-small"
            ),
        )


@dataclass
class RedisConfig:
    """Configuration for Redis Cloud memory store"""

    connection_string: str
    vector_size: int = 1536  # text-embedding-3-small vector size
    collection_name: str = "msa_knowledge"

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create configuration from environment variables"""
        connection_string = os.getenv("REDIS_URL")

        if not connection_string:
            raise ValueError("REDIS_URL must be set")

        return cls(
            connection_string=connection_string,
            vector_size=int(os.getenv("REDIS_VECTOR_SIZE", "1536")),
            collection_name=os.getenv("REDIS_COLLECTION_NAME", "msa_knowledge"),
        )


@dataclass
class DaytonaConfig:
    """Configuration for Daytona Cloud sandbox"""

    endpoint: str
    api_key: str
    workspace_name: str = "msa-reasoning"

    @classmethod
    def from_env(cls) -> "DaytonaConfig":
        """Create configuration from environment variables"""
        endpoint = os.getenv("DAYTONA_ENDPOINT")
        api_key = os.getenv("DAYTONA_API_KEY")

        if not endpoint or not api_key:
            raise ValueError("DAYTONA_ENDPOINT and DAYTONA_API_KEY must be set")

        return cls(
            endpoint=endpoint, api_key=api_key, workspace_name=os.getenv("DAYTONA_WORKSPACE_NAME", "msa-reasoning")
        )


@dataclass
class MSAConfig:
    """Main configuration for MSA system"""

    azure_config: AzureOpenAIConfig
    redis_config: Optional[RedisConfig] = None
    daytona_config: Optional[DaytonaConfig] = None

    # MSA-specific settings
    max_pipeline_steps: int = 10
    confidence_threshold: float = 0.7
    enable_caching: bool = True

    @classmethod
    def from_env(cls) -> "MSAConfig":
        """Create full MSA configuration from environment variables"""
        azure_config = AzureOpenAIConfig.from_env()

        redis_config = None
        try:
            redis_config = RedisConfig.from_env()
        except ValueError:
            pass  # Redis is optional

        daytona_config = None
        try:
            daytona_config = DaytonaConfig.from_env()
        except ValueError:
            pass  # Daytona is optional for basic functionality

        return cls(
            azure_config=azure_config,
            redis_config=redis_config,
            daytona_config=daytona_config,
            max_pipeline_steps=int(os.getenv("MSA_MAX_PIPELINE_STEPS", "10")),
            confidence_threshold=float(os.getenv("MSA_CONFIDENCE_THRESHOLD", "0.7")),
            enable_caching=os.getenv("MSA_ENABLE_CACHING", "true").lower() == "true",
        )
