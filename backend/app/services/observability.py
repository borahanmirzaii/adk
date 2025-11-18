"""Langfuse observability service"""

from typing import Optional, Dict, Any
from langfuse import Langfuse
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ObservabilityService:
    """Service for Langfuse observability"""

    def __init__(self):
        """Initialize Langfuse client"""
        self.langfuse: Optional[Langfuse] = None

        if settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            try:
                self.langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
                logger.info("Langfuse observability enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
        else:
            logger.warning("Langfuse not configured, observability disabled")

    def trace(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Create a new trace"""
        if not self.langfuse:
            return NoneTrace()

        try:
            return self.langfuse.trace(name=name, metadata=metadata or {})
        except Exception as e:
            logger.error(f"Error creating trace: {e}")
            return NoneTrace()

    def is_enabled(self) -> bool:
        """Check if observability is enabled"""
        return self.langfuse is not None


class NoneTrace:
    """Null object for traces when Langfuse is disabled"""

    def span(self, *args, **kwargs):
        return NoneSpan()

    def event(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


class NoneSpan:
    """Null object for spans when Langfuse is disabled"""

    def end(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass


# Global observability service instance
observability_service = ObservabilityService()

