"""Webhook endpoints for n8n integration"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
from pydantic import BaseModel
from app.middleware.auth import require_api_key

router = APIRouter()


class WebhookPayload(BaseModel):
    """Webhook payload model"""
    event: str
    data: Dict[str, Any]


@router.post("/n8n")
async def n8n_webhook(
    request: Request,
    _: bool = Depends(require_api_key())
) -> Dict[str, str]:
    """Receive webhooks from n8n (requires API key)"""
    try:
        payload = await request.json()
        # TODO: Process webhook payload
        return {"status": "received", "message": "Webhook processed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook payload: {str(e)}")


@router.post("/alerts")
async def alert_webhook(
    payload: WebhookPayload,
    request: Request,
    _: bool = Depends(require_api_key())
) -> Dict[str, str]:
    """Receive alert webhooks (requires API key)"""
    # TODO: Process alerts and trigger appropriate actions
    return {"status": "received", "message": "Alert processed"}

