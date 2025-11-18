"""Test cases for Infrastructure Monitor Agent"""

from app.tests.eval.agent_evaluator import TestCase


# Test cases for infrastructure monitoring
INFRASTRUCTURE_TEST_CASES = [
    TestCase(
        name="check_docker_status",
        question="What is the status of Docker containers?",
        expected_answer="docker",
        ground_truth="The agent should check Docker container status and report running/stopped containers."
    ),
    TestCase(
        name="check_disk_space",
        question="How much disk space is available?",
        expected_answer="disk",
        ground_truth="The agent should check disk space usage and report available space."
    ),
    TestCase(
        name="check_memory_usage",
        question="What is the current memory usage?",
        expected_answer="memory",
        ground_truth="The agent should check memory usage and report current consumption."
    ),
    TestCase(
        name="check_database_connection",
        question="Is the database connection healthy?",
        expected_answer="database",
        ground_truth="The agent should check database connection status and report health."
    ),
]

