#!/usr/bin/env python3
"""Run agent evaluation"""

import asyncio
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.infrastructure_monitor import InfrastructureMonitorAgent
from app.tests.eval.agent_evaluator import AgentEvaluator
from app.tests.eval.test_cases.infrastructure_monitor import INFRASTRUCTURE_TEST_CASES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run evaluation"""
    logger.info("Starting agent evaluation...")
    
    # Create evaluator
    evaluator = AgentEvaluator()
    
    # Add test cases
    for test_case in INFRASTRUCTURE_TEST_CASES:
        evaluator.add_test_case(test_case)
    
    # Create agent
    agent = InfrastructureMonitorAgent()
    
    # Run evaluation
    logger.info(f"Evaluating agent: {agent.agent_name}")
    logger.info(f"Test cases: {len(evaluator.test_cases)}")
    
    results = evaluator.evaluate_agent(agent)
    
    # Generate report
    report = evaluator.generate_report(results)
    
    # Print report
    print("\n" + "="*80)
    print("EVALUATION REPORT")
    print("="*80)
    print(f"Agent: {agent.agent_name}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Pass Rate: {report['pass_rate']:.2%}")
    print("\nAverage Metrics:")
    for metric, value in report['average_metrics'].items():
        print(f"  {metric}: {value:.3f}")
    print("\nTest Results:")
    for result in report['results']:
        status = "✓" if result['passed'] else "✗"
        print(f"  {status} {result['test_case']}")
        if result['metrics']:
            for metric, value in result['metrics'].items():
                print(f"    {metric}: {value:.3f}")
        if result['error']:
            print(f"    Error: {result['error']}")
    print("="*80)
    
    # Save report to file
    report_file = Path(__file__).parent.parent / "evaluation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to: {report_file}")
    
    # Exit with error code if any tests failed
    if report['failed'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())

