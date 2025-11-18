"""Health check endpoints"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import httpx
import redis
from app.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check"""
    return {"status": "healthy", "service": "adk-devops-assistant"}


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check for all services"""
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "services": {},
    }

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check Supabase
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/",
                timeout=5.0,
            )
            if response.status_code == 200:
                health_status["services"]["supabase"] = {"status": "healthy"}
            else:
                health_status["services"]["supabase"] = {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}",
                }
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["supabase"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"

    # Check Langfuse (optional)
    if settings.LANGFUSE_PUBLIC_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.LANGFUSE_HOST}/api/public/health",
                    timeout=5.0,
                )
                if response.status_code == 200:
                    health_status["services"]["langfuse"] = {"status": "healthy"}
                else:
                    health_status["services"]["langfuse"] = {
                        "status": "unhealthy",
                        "error": f"Status code: {response.status_code}",
                    }
        except Exception as e:
            health_status["services"]["langfuse"] = {
                "status": "unhealthy",
                "error": str(e),
            }

    # Check n8n (optional)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                settings.N8N_WEBHOOK_URL.replace("/webhook", "/healthz"),
                timeout=5.0,
            )
            if response.status_code == 200:
                health_status["services"]["n8n"] = {"status": "healthy"}
            else:
                health_status["services"]["n8n"] = {
                    "status": "unhealthy",
                    "error": f"Status code: {response.status_code}",
                }
    except Exception as e:
        health_status["services"]["n8n"] = {"status": "unhealthy", "error": str(e)}

    if health_status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

