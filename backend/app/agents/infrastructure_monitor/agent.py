"""Infrastructure Monitor Agent"""

import asyncio
from typing import Optional
from google.adk.tools import FunctionTool
from app.agents.base_agent import BaseADKAgent
from app.agents.infrastructure_monitor.tools import (
    check_docker_containers,
    check_disk_space,
    check_memory_usage,
    check_database_connection,
)
from app.agents.infrastructure_monitor.prompts import SYSTEM_PROMPT
from app.services.n8n_service import n8n_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class InfrastructureMonitorAgent(BaseADKAgent):
    """Agent for monitoring infrastructure"""

    def __init__(self):
        """Initialize Infrastructure Monitor Agent"""
        # Create tools
        tools = [
            FunctionTool(
                name="check_docker_containers",
                func=check_docker_containers,
                description="Check status of all Docker containers",
            ),
            FunctionTool(
                name="check_disk_space",
                func=check_disk_space,
                description="Check disk space usage",
            ),
            FunctionTool(
                name="check_memory_usage",
                func=check_memory_usage,
                description="Check memory usage",
            ),
            FunctionTool(
                name="check_database_connection",
                func=check_database_connection,
                description="Check database connection status",
            ),
        ]

        super().__init__(
            agent_name="infrastructure_monitor",
            system_prompt=SYSTEM_PROMPT,
            tools=tools,
        )

    async def monitor_services(self) -> dict:
        """Monitor all services and store metrics"""
        try:
            # Check all services
            docker_status = check_docker_containers()
            disk_status = check_disk_space()
            memory_status = check_memory_usage()
            db_status = check_database_connection()

            # Store metrics in Supabase
            metrics = [
                {
                    "service_name": "docker",
                    "metric_type": "container_count",
                    "metric_value": docker_status.get("running", 0),
                    "status": "healthy" if docker_status.get("running", 0) > 0 else "warning",
                    "metadata": docker_status,
                },
                {
                    "service_name": "disk",
                    "metric_type": "usage_percent",
                    "metric_value": disk_status.get("percent_used", 0),
                    "unit": "percent",
                    "status": (
                        "critical" if disk_status.get("percent_used", 0) > 90
                        else "warning" if disk_status.get("percent_used", 0) > 75
                        else "healthy"
                    ),
                    "metadata": disk_status,
                },
                {
                    "service_name": "memory",
                    "metric_type": "usage_percent",
                    "metric_value": memory_status.get("percent_used", 0),
                    "unit": "percent",
                    "status": (
                        "critical" if memory_status.get("percent_used", 0) > 90
                        else "warning" if memory_status.get("percent_used", 0) > 75
                        else "healthy"
                    ),
                    "metadata": memory_status,
                },
            ]

            # Store in database
            for metric in metrics:
                self.supabase.table("infrastructure_metrics").insert(metric).execute()

            # Check for critical issues and send alerts
            critical_metrics = [m for m in metrics if m["status"] == "critical"]
            if critical_metrics:
                await n8n_service.send_alert(
                    alert_type="infrastructure_critical",
                    message=f"Critical issues detected: {[m['service_name'] for m in critical_metrics]}",
                    severity="critical",
                    metadata={"metrics": critical_metrics},
                )

            # Update agent status
            await self.update_status(
                status="running",
                metrics={
                    "docker": docker_status,
                    "disk": disk_status,
                    "memory": memory_status,
                    "database": db_status,
                },
            )

            return {
                "status": "success",
                "metrics": metrics,
                "summary": {
                    "docker": docker_status,
                    "disk": disk_status,
                    "memory": memory_status,
                    "database": db_status,
                },
            }

        except Exception as e:
            logger.error(f"Error monitoring services: {e}", exc_info=True)
            await self.update_status(status="error", metrics={"error": str(e)})
            raise


# Global agent instance
infrastructure_monitor_agent = InfrastructureMonitorAgent()


async def main():
    """Main function for running agent in CLI mode"""
    agent = InfrastructureMonitorAgent()
    result = await agent.monitor_services()
    print(f"Monitoring complete: {result}")


if __name__ == "__main__":
    asyncio.run(main())

