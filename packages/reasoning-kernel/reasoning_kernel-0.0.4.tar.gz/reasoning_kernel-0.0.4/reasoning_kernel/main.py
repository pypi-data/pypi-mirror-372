"""
Main FastAPI application entry point for MSA Reasoning Engine
"""

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from reasoning_kernel.core.env import load_project_dotenv
from reasoning_kernel.core.config_manager import get_config
from reasoning_kernel.core.logging_config import configure_logging, get_logger
from reasoning_kernel.middleware.logging import RequestLoggingMiddleware
from reasoning_kernel.core.lifespan import lifespan

# Load environment variables
load_project_dotenv(override=False)

# Get configuration using config_manager
settings = get_config()

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=str(settings.version),
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)


def include_router(router, **kwargs):
    """Safely includes a router."""
    if router:
        app.include_router(router, **kwargs)
    else:
        logger.warning(f"Router for prefix {kwargs.get('prefix')} is not available.")


# Register routers
def register_routers():
    """Registers all the application routers."""
    from reasoning_kernel.api.health_endpoints import router as health_router
    from reasoning_kernel.api.memory_endpoints import router as memory_router
    from reasoning_kernel.api.redis_endpoints import router as redis_router
    from reasoning_kernel.api.endpoints import router as endpoints_router
    from reasoning_kernel.api.msa_endpoints import router as msa_router
    
    # Optional routers with fallback handling
    try:
        from reasoning_kernel.api.confidence_endpoints import confidence_router
    except ImportError:
        confidence_router = None
    
    try:
        from reasoning_kernel.api.annotation_endpoints import router as annotation_router
    except ImportError:
        annotation_router = None
    
    try:
        from reasoning_kernel.api.model_olympics import router as model_olympics_router
    except ImportError:
        model_olympics_router = None
    
    # v2 API imports (may not be available)
    v2_router = None
    daytona_router = None
    v2_health_router = None
    v2_visualization_router = None
    prob_viz_router = None
    streaming_router = None
    
    try:
        from reasoning_kernel.api.reasoning_endpoints import router as v2_router_local
        v2_router = v2_router_local
    except ImportError:
        pass
    
    try:
        from reasoning_kernel.api.daytona_endpoints import router as daytona_router_local
        daytona_router = daytona_router_local
    except ImportError:
        pass
    
    try:
        from reasoning_kernel.api.health_endpoints import router as v2_health_router_local
        v2_health_router = v2_health_router_local
    except ImportError:
        pass
    
    try:
        from reasoning_kernel.api.visualization_endpoints import router as v2_visualization_router_local
        v2_visualization_router = v2_visualization_router_local
    except ImportError:
        pass
    
    try:
        from reasoning_kernel.api.probability_visualization_endpoints import router as prob_viz_router_local
        prob_viz_router = prob_viz_router_local
    except ImportError:
        pass
    
    try:
        from reasoning_kernel.api.streaming_endpoints import router as streaming_router_local
        streaming_router = streaming_router_local
    except ImportError:
        pass

    # v1 routers
    include_router(health_router, prefix="/api/v1")
    include_router(redis_router, prefix="/api/v1")
    include_router(memory_router, prefix="/api/v1")
    include_router(endpoints_router, prefix="/api/v1")
    include_router(msa_router, prefix="/api/v1")
    
    if confidence_router is not None:
        include_router(confidence_router, prefix="/api/v1")
    
    if annotation_router is not None:
        include_router(annotation_router)
    
    if model_olympics_router is not None:
        include_router(model_olympics_router)

    # v2 routers (only include if available)
    if v2_router is not None:
        include_router(v2_router)
    
    if daytona_router is not None:
        include_router(daytona_router, prefix="/api/v2")
    
    if v2_health_router is not None:
        include_router(v2_health_router, prefix="/api/v2")
    
    if v2_visualization_router is not None:
        include_router(v2_visualization_router, prefix="/api/v2")
    
    if prob_viz_router is not None:
        include_router(prob_viz_router)
    
    if streaming_router is not None:
        include_router(streaming_router)


register_routers()

# Mount static files
if os.path.exists("reasoning_kernel/static"):
    app.mount("/static", StaticFiles(directory="reasoning_kernel/static"), name="static")


# Root and UI endpoints
@app.get("/")
async def root():
    """Root returns system info (JSON) for tests & clients."""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "operational",
    }


@app.get("/ui")
async def ui():
    """Serve the real-time streaming interface HTML."""
    return FileResponse("reasoning_kernel/static/realtime-streaming.html", media_type="text/html")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler with structured logging."""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "reasoning_kernel.main:app",
        host="0.0.0.0",
        port=5000,
        reload=os.getenv("DEVELOPMENT", "false").lower() == "true",
        log_level="info",
    )


if __name__ == "__main__":
    run_server()