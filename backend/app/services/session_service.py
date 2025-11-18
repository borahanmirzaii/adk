"""Supabase session management service"""

from typing import Optional, Dict, Any
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing ADK sessions in Supabase"""

    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
        )

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session from Supabase"""
        try:
            response = (
                self.supabase.table("adk_sessions")
                .select("*")
                .eq("session_id", session_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {e}")
            return None

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        app_name: str = "adk-devops-assistant",
        initial_state: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new session with tenant isolation"""
        try:
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "app_name": app_name,
                "state": initial_state or {},
                "events": [],
            }
            # Add tenant_id if provided (for multi-tenancy)
            if tenant_id:
                session_data["tenant_id"] = tenant_id
            
            response = self.supabase.table("adk_sessions").insert(session_data).execute()
            return response.data[0] if response.data else session_data
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            raise

    async def update_session_state(
        self, session_id: str, state: Dict[str, Any]
    ) -> bool:
        """Update session state"""
        try:
            self.supabase.table("adk_sessions").update({"state": state}).eq(
                "session_id", session_id
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating session state {session_id}: {e}")
            return False

    async def add_event(
        self, session_id: str, event: Dict[str, Any]
    ) -> bool:
        """Add event to session history"""
        try:
            # Get current events
            session = await self.get_session(session_id)
            if not session:
                return False

            events = session.get("events", [])
            events.append(event)

            # Update events
            self.supabase.table("adk_sessions").update({"events": events}).eq(
                "session_id", session_id
            ).execute()

            # Also save to session_history table
            self.supabase.table("session_history").insert(
                {
                    "session_id": session_id,
                    "user_message": event.get("user_message", ""),
                    "agent_response": event.get("agent_response", ""),
                    "agent_name": event.get("agent_name", "unknown"),
                    "metadata": event.get("metadata", {}),
                }
            ).execute()

            return True
        except Exception as e:
            logger.error(f"Error adding event to session {session_id}: {e}")
            return False

    async def get_session_history(
        self, session_id: str, limit: int = 50
    ) -> list[Dict[str, Any]]:
        """Get session history"""
        try:
            response = (
                self.supabase.table("session_history")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error retrieving session history {session_id}: {e}")
            return []


# Global session service instance
session_service = SessionService()

