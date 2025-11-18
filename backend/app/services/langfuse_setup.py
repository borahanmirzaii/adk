"""OpenTelemetry setup for Langfuse integration"""

import logging
import os
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from langfuse.opentelemetry import LangfuseSpanProcessor
from openinference.instrumentation.google_adk import GoogleADKInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from app.config import settings

logger = logging.getLogger(__name__)


def setup_opentelemetry(app=None) -> bool:
    """
    Setup OpenTelemetry instrumentation for Langfuse
    
    Args:
        app: Optional FastAPI app to instrument
    
    Returns:
        True if setup successful, False otherwise
    """
    if not settings.LANGFUSE_PUBLIC_KEY or not settings.LANGFUSE_SECRET_KEY:
        logger.warning("Langfuse keys not configured, OpenTelemetry not initialized")
        return False
    
    try:
        # Create resource with service name
        resource = Resource.create({
            "service.name": settings.APP_NAME,
            "service.version": "0.1.0",
        })
        
        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Add Langfuse span processor
        langfuse_processor = LangfuseSpanProcessor(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
        
        tracer_provider.add_span_processor(
            BatchSpanProcessor(langfuse_processor)
        )
        
        # Instrument Google ADK
        GoogleADKInstrumentor().instrument()
        logger.info("Google ADK instrumentation enabled")
        
        # Instrument FastAPI if app provided
        if app:
            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI instrumentation enabled")
        
        # Instrument HTTPX client
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX client instrumentation enabled")
        
        logger.info("OpenTelemetry setup complete for Langfuse")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry: {e}", exc_info=True)
        return False


def shutdown_opentelemetry():
    """Shutdown OpenTelemetry instrumentation"""
    try:
        # Shutdown tracer provider
        tracer_provider = trace.get_tracer_provider()
        if hasattr(tracer_provider, 'shutdown'):
            tracer_provider.shutdown()
        logger.info("OpenTelemetry shutdown complete")
    except Exception as e:
        logger.error(f"Error shutting down OpenTelemetry: {e}")

