"""Start all agents in monitoring mode"""

import asyncio
import logging
from app.agents.infrastructure_monitor import InfrastructureMonitorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_monitoring():
    """Start infrastructure monitoring"""
    agent = InfrastructureMonitorAgent()
    
    while True:
        try:
            result = await agent.monitor_services()
            logger.info(f"Monitoring complete: {result['status']}")
            await asyncio.sleep(30)  # Monitor every 30 seconds
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            await asyncio.sleep(60)  # Wait longer on error


if __name__ == "__main__":
    asyncio.run(start_monitoring())

