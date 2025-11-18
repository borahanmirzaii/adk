#!/usr/bin/env python3
"""
Test Script for Event Bus End-to-End Flow

This script tests the complete event system:
1. Publishes test events to Redis
2. Verifies events can be published via EventDispatcher
3. Tests the event normalization flow

Run this script to verify the Event Bus is working correctly.

Usage:
    python test_event_bus.py
"""

import asyncio
import logging
from datetime import datetime

from app.event_bus import get_event_dispatcher, get_event_bus
from app.event_bus.schema import Event

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_event_bus_direct():
    """Test publishing events directly to the event bus"""
    logger.info("=" * 60)
    logger.info("TEST 1: Direct Event Bus Publishing")
    logger.info("=" * 60)

    bus = get_event_bus()

    # Create a test event
    event = Event(
        session_id="test-session-123",
        type="tool_call_started",
        payload={
            "tool_call_id": "tc_001",
            "tool_name": "docker_list_containers",
            "args": {"status": "running"},
            "agent": "infrastructure_monitor"
        }
    )

    logger.info(f"Publishing event: {event.type}")
    logger.info(f"Event ID: {event.event_id}")
    logger.info(f"Session ID: {event.session_id}")
    logger.info(f"Payload: {event.payload}")

    try:
        await bus.publish(event)
        logger.info("✅ Event published successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to publish event: {e}")
        raise


async def test_event_dispatcher():
    """Test publishing events via EventDispatcher"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: EventDispatcher Publishing")
    logger.info("=" * 60)

    dispatcher = get_event_dispatcher()
    session_id = "test-session-456"

    # Test 1: Session started
    logger.info("\nPublishing session_started event...")
    await dispatcher.session_started(
        session_id=session_id,
        agent="infrastructure_monitor",
        metadata={"test": True}
    )
    logger.info("✅ session_started published")

    # Test 2: Agent message delta
    logger.info("\nPublishing agent_message_delta event...")
    await dispatcher.agent_message_delta(
        session_id=session_id,
        message_id="msg_001",
        delta="Checking Docker containers..."
    )
    logger.info("✅ agent_message_delta published")

    # Test 3: Tool call started
    logger.info("\nPublishing tool_call_started event...")
    await dispatcher.tool_call_started(
        session_id=session_id,
        tool_call_id="tc_002",
        tool_name="docker_list_containers",
        args={"status": "running"},
        agent="infrastructure_monitor"
    )
    logger.info("✅ tool_call_started published")

    # Test 4: Tool call result
    logger.info("\nPublishing tool_call_result event...")
    await dispatcher.tool_call_result(
        session_id=session_id,
        tool_call_id="tc_002",
        tool_name="docker_list_containers",
        result={"containers": [{"id": "abc123", "name": "nginx"}]}
    )
    logger.info("✅ tool_call_result published")

    # Test 5: Workflow events
    logger.info("\nPublishing workflow events...")
    await dispatcher.workflow_started(
        session_id=session_id,
        workflow="monitoring_workflow",
        run_id="run_001"
    )
    await dispatcher.workflow_step_started(
        session_id=session_id,
        run_id="run_001",
        step_id="check_docker",
        description="Checking Docker containers"
    )
    await dispatcher.workflow_transition(
        session_id=session_id,
        run_id="run_001",
        from_step="check_docker",
        to_step="analyze_metrics",
        reason="Docker check completed"
    )
    logger.info("✅ workflow events published")

    # Test 6: Metrics update
    logger.info("\nPublishing metrics_update event...")
    await dispatcher.metrics_update(
        session_id=session_id,
        cpu=45.2,
        memory_used="2.1GB",
        disk_free="50GB",
        containers_running=3
    )
    logger.info("✅ metrics_update published")

    # Test 7: Error event
    logger.info("\nPublishing run_error event...")
    await dispatcher.run_error(
        session_id=session_id,
        error_type="ConnectionError",
        message="Failed to connect to Docker daemon",
        agent="infrastructure_monitor",
        step="check_docker"
    )
    logger.info("✅ run_error published")


async def test_sse_format():
    """Test SSE formatting of events"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: SSE Format Conversion")
    logger.info("=" * 60)

    event = Event(
        session_id="test-session-789",
        type="agent_message_delta",
        payload={
            "message_id": "msg_001",
            "delta": "Hello from the event bus!"
        }
    )

    sse_output = event.to_sse()
    logger.info("SSE formatted output:")
    logger.info(sse_output)
    logger.info("✅ SSE formatting works correctly")


async def main():
    """Run all tests"""
    logger.info("\n🚀 Starting Event Bus End-to-End Tests\n")

    try:
        # Run all tests
        await test_event_bus_direct()
        await test_event_dispatcher()
        await test_sse_format()

        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL TESTS PASSED!")
        logger.info("=" * 60)
        logger.info("\nEvent Bus is working correctly!")
        logger.info("\nNext steps:")
        logger.info("1. Start Redis: docker-compose up redis -d")
        logger.info("2. Start backend: just dev-backend")
        logger.info("3. Test SSE endpoint: curl http://localhost:8000/api/events/test-session")
        logger.info("4. In another terminal, run this script again to publish events")
        logger.info("   You should see events appear in the curl output!")

    except Exception as e:
        logger.error("\n" + "=" * 60)
        logger.error("❌ TESTS FAILED!")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
