"""Evaluation metrics and scoring functions"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """Calculate various evaluation metrics"""

    @staticmethod
    def calculate_faithfulness_score(answer: str, context: List[str]) -> float:
        """
        Calculate faithfulness score (how well answer is supported by context)
        
        Args:
            answer: Agent's answer
            context: Context used to generate answer
        
        Returns:
            Score between 0 and 1
        """
        # Simple implementation - check if answer keywords appear in context
        if not context:
            return 0.0
        
        answer_words = set(answer.lower().split())
        context_text = " ".join(context).lower()
        context_words = set(context_text.split())
        
        overlap = len(answer_words & context_words)
        total_answer_words = len(answer_words)
        
        if total_answer_words == 0:
            return 0.0
        
        return min(overlap / total_answer_words, 1.0)

    @staticmethod
    def calculate_relevancy_score(question: str, answer: str) -> float:
        """
        Calculate answer relevancy score
        
        Args:
            question: Original question
            answer: Agent's answer
        
        Returns:
            Score between 0 and 1
        """
        # Simple implementation - check keyword overlap
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been"}
        question_words = question_words - stop_words
        answer_words = answer_words - stop_words
        
        if not question_words:
            return 0.0
        
        overlap = len(question_words & answer_words)
        return min(overlap / len(question_words), 1.0)

    @staticmethod
    def calculate_precision_score(expected: str, actual: str) -> float:
        """
        Calculate precision score
        
        Args:
            expected: Expected answer
            actual: Actual answer
        
        Returns:
            Score between 0 and 1
        """
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not actual_words:
            return 0.0
        
        overlap = len(expected_words & actual_words)
        return min(overlap / len(actual_words), 1.0)

    @staticmethod
    def calculate_recall_score(expected: str, actual: str) -> float:
        """
        Calculate recall score
        
        Args:
            expected: Expected answer
            actual: Actual answer
        
        Returns:
            Score between 0 and 1
        """
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            return 0.0
        
        overlap = len(expected_words & actual_words)
        return min(overlap / len(expected_words), 1.0)

    @staticmethod
    def calculate_f1_score(expected: str, actual: str) -> float:
        """
        Calculate F1 score (harmonic mean of precision and recall)
        
        Args:
            expected: Expected answer
            actual: Actual answer
        
        Returns:
            F1 score between 0 and 1
        """
        precision = MetricsCalculator.calculate_precision_score(expected, actual)
        recall = MetricsCalculator.calculate_recall_score(expected, actual)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)

