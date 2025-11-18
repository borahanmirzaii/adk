"""Agent evaluation framework using Ragas"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from app.agents.base_agent import BaseADKAgent

logger = logging.getLogger(__name__)

try:
    from ragas import evaluate
    from ragas.metrics import (
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    )
    from datasets import Dataset
    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False
    logger.warning("Ragas not available. Install with: pip install ragas")


@dataclass
class EvaluationResult:
    """Result of agent evaluation"""
    agent_name: str
    test_case_name: str
    metrics: Dict[str, float]
    passed: bool
    error: Optional[str] = None


@dataclass
class TestCase:
    """Test case for agent evaluation"""
    name: str
    question: str
    expected_answer: Optional[str] = None
    context: Optional[List[str]] = None
    ground_truth: Optional[str] = None


class AgentEvaluator:
    """Framework for evaluating agent performance"""

    def __init__(self):
        """Initialize evaluator"""
        if not RAGAS_AVAILABLE:
            logger.warning("Ragas not available. Evaluation will be limited.")
        self.test_cases: List[TestCase] = []

    def add_test_case(self, test_case: TestCase):
        """Add a test case to the evaluator"""
        self.test_cases.append(test_case)

    def evaluate_agent(
        self,
        agent: BaseADKAgent,
        test_cases: Optional[List[TestCase]] = None
    ) -> List[EvaluationResult]:
        """
        Evaluate an agent against test cases
        
        Args:
            agent: Agent to evaluate
            test_cases: Optional list of test cases (uses self.test_cases if not provided)
        
        Returns:
            List of evaluation results
        """
        test_cases = test_cases or self.test_cases
        
        if not test_cases:
            logger.warning("No test cases provided for evaluation")
            return []
        
        results = []
        
        for test_case in test_cases:
            try:
                # Execute agent
                response = agent.execute(test_case.question)
                
                # Prepare data for Ragas evaluation
                if RAGAS_AVAILABLE and test_case.ground_truth:
                    metrics = self._evaluate_with_ragas(
                        question=test_case.question,
                        answer=response,
                        ground_truth=test_case.ground_truth,
                        context=test_case.context or []
                    )
                else:
                    # Basic evaluation without Ragas
                    metrics = self._basic_evaluation(
                        question=test_case.question,
                        answer=response,
                        expected=test_case.expected_answer
                    )
                
                # Determine if test passed
                passed = self._check_pass_criteria(metrics)
                
                result = EvaluationResult(
                    agent_name=agent.agent_name,
                    test_case_name=test_case.name,
                    metrics=metrics,
                    passed=passed
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error evaluating test case {test_case.name}: {e}")
                result = EvaluationResult(
                    agent_name=agent.agent_name,
                    test_case_name=test_case.name,
                    metrics={},
                    passed=False,
                    error=str(e)
                )
                results.append(result)
        
        return results

    def _evaluate_with_ragas(
        self,
        question: str,
        answer: str,
        ground_truth: str,
        context: List[str]
    ) -> Dict[str, float]:
        """Evaluate using Ragas metrics"""
        if not RAGAS_AVAILABLE:
            return {}
        
        try:
            # Prepare dataset for Ragas
            dataset = Dataset.from_dict({
                "question": [question],
                "answer": [answer],
                "ground_truth": [ground_truth],
                "contexts": [context] if context else [[]],
            })
            
            # Run evaluation
            result = evaluate(
                dataset,
                metrics=[
                    faithfulness,
                    answer_relevancy,
                    context_precision,
                    context_recall,
                ]
            )
            
            # Extract metrics
            metrics = {
                "faithfulness": result["faithfulness"][0] if "faithfulness" in result else 0.0,
                "answer_relevancy": result["answer_relevancy"][0] if "answer_relevancy" in result else 0.0,
                "context_precision": result["context_precision"][0] if "context_precision" in result else 0.0,
                "context_recall": result["context_recall"][0] if "context_recall" in result else 0.0,
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error in Ragas evaluation: {e}")
            return {}

    def _basic_evaluation(
        self,
        question: str,
        answer: str,
        expected: Optional[str]
    ) -> Dict[str, float]:
        """Basic evaluation without Ragas"""
        metrics = {
            "answer_length": len(answer),
            "question_length": len(question),
        }
        
        if expected:
            # Simple similarity check
            answer_lower = answer.lower()
            expected_lower = expected.lower()
            
            # Check if expected keywords are in answer
            expected_words = set(expected_lower.split())
            answer_words = set(answer_lower.split())
            overlap = len(expected_words & answer_words)
            similarity = overlap / len(expected_words) if expected_words else 0.0
            
            metrics["similarity"] = similarity
        
        return metrics

    def _check_pass_criteria(self, metrics: Dict[str, float]) -> bool:
        """Check if metrics meet pass criteria"""
        if not metrics:
            return False
        
        # Default pass criteria
        min_faithfulness = 0.7
        min_relevancy = 0.7
        
        faithfulness_score = metrics.get("faithfulness", 0.0)
        relevancy_score = metrics.get("answer_relevancy", 0.0)
        
        # If Ragas metrics available, use them
        if "faithfulness" in metrics or "answer_relevancy" in metrics:
            return (
                faithfulness_score >= min_faithfulness and
                relevancy_score >= min_relevancy
            )
        
        # Otherwise, use basic metrics
        similarity = metrics.get("similarity", 0.0)
        return similarity >= 0.5

    def generate_report(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Generate evaluation report"""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        
        # Calculate average metrics
        avg_metrics = {}
        if results and results[0].metrics:
            for key in results[0].metrics.keys():
                values = [r.metrics.get(key, 0.0) for r in results if key in r.metrics]
                if values:
                    avg_metrics[key] = sum(values) / len(values)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0.0,
            "average_metrics": avg_metrics,
            "results": [
                {
                    "test_case": r.test_case_name,
                    "passed": r.passed,
                    "metrics": r.metrics,
                    "error": r.error
                }
                for r in results
            ]
        }

