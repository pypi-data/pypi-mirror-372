"""
Manages the application lifecycle with a modular lifespan function.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
import structlog
import re

from ..core.config_manager import get_config
from ..security.security_manager import SecurityConfig, setup_security, security_manager
from ..core.kernel_manager import KernelManager
from ..database.connection import init_database
from ..msa.synthesis_engine import MSAEngine
from ..services.unified_redis_service import create_unified_redis_service as create_redis_services

logger = structlog.get_logger(__name__)

# Global instances
kernel_manager = None
msa_engine = None
reasoning_kernel = None
redis_memory_service = None
redis_retrieval_service = None
db_manager = None
security_manager_global = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events
    """
    global kernel_manager, msa_engine, reasoning_kernel, redis_memory_service, redis_retrieval_service, db_manager, security_manager_global

    logger.info("🚀 Starting MSA Reasoning Engine...")
    try:
        if os.getenv("PYTEST_CURRENT_TEST"):
            logger.info("Test mode detected - skipping heavy initialization")
            yield
            return

        await initialize_security(app)
        await initialize_services(app)

        logger.info("🎯 MSA Reasoning Engine ready for requests")
        yield

    except Exception as e:
        logger.error(f"❌ Failed to initialize MSA Engine: {e}")
        raise
    finally:
        await cleanup_services()
        logger.info("✅ Shutdown complete")


async def initialize_security(app: FastAPI):
    """Initializes the security system."""
    try:
        logger.info("🔒 Initializing security system...")
        security_config = SecurityConfig.from_env()
        await setup_security(app, security_config)
        globals()["security_manager_global"] = security_manager
        app.state.security_manager = security_manager
        logger.info("✅ Security system initialized")
    except Exception as sec_err:
        logger.warning(f"Security system not initialized (optional): {sec_err}")
        globals()["security_manager_global"] = None
        app.state.security_manager = None


async def initialize_services(app: FastAPI):
    """Initializes the core services of the application."""
    global kernel_manager, msa_engine, reasoning_kernel, redis_memory_service, redis_retrieval_service, db_manager

    # Initialize Redis
    redis_memory_service, redis_retrieval_service = await initialize_redis()
    app.state.redis_memory = redis_memory_service
    app.state.redis_retrieval = redis_retrieval_service

    # Initialize Database
    db_manager = init_database()
    app.state.db_manager = db_manager
    logger.info("✅ PostgreSQL database initialized")

    # Initialize Kernel
    kernel_manager = await initialize_kernel()
    app.state.kernel_manager = kernel_manager

    # Initialize MSA Engine
    msa_engine = await initialize_msa_engine(kernel_manager, redis_memory_service, redis_retrieval_service)
    app.state.msa_engine = msa_engine

    # Initialize Reasoning Kernel
    reasoning_kernel = await initialize_reasoning_kernel(kernel_manager, redis_memory_service)
    app.state.reasoning_kernel = reasoning_kernel


async def initialize_redis():
    """Initializes and returns Redis services."""
    config = get_config()
    redis_url_clean = config.redis_url
    if "export" in redis_url_clean and "redis://" in redis_url_clean:
        match = re.search(r"redis://[^\s\'\"]+", redis_url_clean)
        if match:
            redis_url_clean = match.group(0)

    logger.info(f"Using Redis URL: {redis_url_clean}")
    redis_service = await create_redis_services(
        redis_url=redis_url_clean,
    )
    logger.info("✅ Redis service initialized")
    # Return the same service instance twice for backward compatibility
    return redis_service, redis_service


async def initialize_kernel():
    """Initializes and returns the KernelManager."""
    km = KernelManager()
    await km.initialize()
    logger.info("✅ Semantic Kernel initialized")
    return km


async def initialize_msa_engine(kernel_manager, memory_service, retrieval_service):
    """Initializes and returns the MSAEngine."""
    engine = MSAEngine(
        kernel_manager,
        memory_service=memory_service,
        retrieval_service=retrieval_service,
    )
    await engine.initialize()
    logger.info("✅ MSA Engine initialized")
    return engine


async def initialize_reasoning_kernel(kernel_manager, memory_service):
    """Initializes and returns the ReasoningKernel."""
    try:
        from reasoning_kernel.reasoning_kernel import ReasoningConfig, ReasoningKernel
        if kernel_manager.kernel:
            rk = ReasoningKernel(
                kernel=kernel_manager.kernel,
                redis_client=memory_service,
                config=ReasoningConfig(),
            )
            logger.info("✅ Reasoning Kernel (v2) initialized")
            return rk
        else:
            logger.warning("Kernel not available, skipping Reasoning Kernel initialization")
            return None
    except Exception as e:
        logger.warning(f"Failed to initialize Reasoning Kernel: {e}")
        return None


async def cleanup_services():
    """Cleans up the services."""
    logger.info("🔄 Shutting down MSA Reasoning Engine...")
    if msa_engine:
        await msa_engine.cleanup()
    if kernel_manager:
        await kernel_manager.cleanup()
    if db_manager:
        db_manager.cleanup()