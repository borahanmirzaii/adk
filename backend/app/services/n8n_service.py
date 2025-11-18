"""n8n workflow service"""

from typing import Dict, Any, Optional
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class N8nService:
    """Service for triggering n8n workflows"""

    def __init__(self):
        """Initialize n8n service"""
        self.webhook_url = settings.N8N_WEBHOOK_URL
        self.api_key = settings.N8N_API_KEY

    async def trigger_webhook(
        self, workflow_id: str, payload: Dict[str, Any]
    ) -> bool:
        """Trigger a n8n webhook"""
        try:
            url = f"{self.webhook_url}/{workflow_id}"
            headers = {}
            if self.api_key:
                headers["X-N8N-API-KEY"] = self.api_key

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Error triggering n8n webhook {workflow_id}: {e}")
            return False

    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "info",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send an alert via n8n"""
        payload = {
            "event": "alert",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "metadata": metadata or {},
        }
        return await self.trigger_webhook("alerts", payload)


# Global n8n service instance
n8n_service = N8nService()

