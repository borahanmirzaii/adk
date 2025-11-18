"""Base agent class with Supabase session, Langfuse tracing, and error handling"""

from typing import Optional, Dict, Any, List
from google.adk.llm_agents import LLMAgent
from google.adk.models import GenerativeModel
from langfuse import Langfuse
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from app.config import settings
from app.services.observability import observability_service
from app.services.session_service import session_service

logger = logging.getLogger(__name__)


class BaseADKAgent:
    """Base class for all ADK agents with built-in integrations"""

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: Optional[List] = None,
    ):
        """
        Initialize base agent

        Args:
            agent_name: Name of the agent
            system_prompt: System prompt for the agent
            tools: List of tools for the agent
        """
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools or []

        # Initialize Supabase client
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_ANON_KEY,
        )

        # Create ADK agent
        try:
            self.agent = LLMAgent(
                name=agent_name,
                model=GenerativeModel(
                    model_name=settings.GEMINI_MODEL,
                    api_key=settings.GOOGLE_API_KEY,
                ),
                system_instruction=system_prompt,
                tools=self.tools,
            )
            logger.info(f"Initialized {agent_name} with {len(self.tools)} tools")
        except Exception as e:
            logger.error(f"Failed to initialize agent {agent_name}: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def execute(
        self, user_message: str, session_id: Optional[str] = None
    ) -> str:
        """
        Execute agent with tracing and session persistence

        Args:
            user_message: User's input
            session_id: Optional session ID for persistence

        Returns:
            Agent's response
        """
        # Start Langfuse trace
        trace = observability_service.trace(
            name=f"{self.agent_name}_execution",
            metadata={"session_id": session_id, "user_message": user_message},
        )

        try:
            # Retrieve or create session
            if session_id:
                session_data = await session_service.get_session(session_id)
                if not session_data:
                    await session_service.create_session(
                        session_id=session_id,
                        user_id="default-user",  # TODO: Get from auth
                    )

            # Execute agent
            if trace:
                span = trace.span(name="agent_execution")
            else:
                span = None

            # Run agent (synchronous for now, async support coming)
            response = self.agent.run(user_message)

            if span:
                span.end(output=response.content if hasattr(response, "content") else str(response))

            response_text = response.content if hasattr(response, "content") else str(response)

            # Save to session
            if session_id:
                await session_service.add_event(
                    session_id=session_id,
                    event={
                        "user_message": user_message,
                        "agent_response": response_text,
                        "agent_name": self.agent_name,
                        "metadata": {},
                    },
                )

            # Log metrics
            if trace:
                trace.event(
                    name="execution_complete",
                    metadata={
                        "message_length": len(user_message),
                        "response_length": len(response_text),
                    },
                )

            return response_text

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            if trace:
                trace.event(name="execution_failed", metadata={"error": str(e)})
            raise

        finally:
            if trace:
                trace.update(status="success")

    async def update_status(
        self, status: str, metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update agent status in database"""
        try:
            self.supabase.table("agent_status").upsert(
                {
                    "agent_name": self.agent_name,
                    "status": status,
                    "metrics": metrics or {},
                }
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating agent status: {e}")
            return False

