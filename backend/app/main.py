"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import health, agents, chat, webhooks, copilotkit, events
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging import setup_logging
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.metrics import MetricsMiddleware, get_metrics
from app.services.langfuse_setup import setup_opentelemetry, shutdown_opentelemetry
from fastapi.responses import Response

# Initialize FastAPI app
app = FastAPI(
    title="ADK Dev Environment Manager API",
    description="API for managing AI agents in development environments",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup OpenTelemetry for Langfuse
setup_opentelemetry(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup middleware
setup_logging(app)
setup_error_handlers(app)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(copilotkit.router, prefix="/api", tags=["copilotkit"])
app.include_router(events.router, prefix="/api", tags=["events"])


@app.get("/api/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "ADK Dev Environment Manager API",
            "version": "0.1.0",
            "docs": "/docs",
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    shutdown_opentelemetry()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )

