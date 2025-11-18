"""Seed database with sample data"""

import asyncio
from supabase import create_client, Client
from app.config import settings


async def seed_database():
    """Seed database with initial data"""
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    # Seed agent status
    agents = [
        {"agent_name": "infrastructure_monitor", "status": "idle"},
        {"agent_name": "code_reviewer", "status": "idle"},
        {"agent_name": "deployment_orchestrator", "status": "idle"},
        {"agent_name": "knowledge_base", "status": "idle"},
    ]

    for agent in agents:
        supabase.table("agent_status").upsert(agent).execute()

    print("✅ Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_database())

