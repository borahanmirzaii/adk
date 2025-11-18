"""Code Reviewer Agent"""

from app.agents.base_agent import BaseADKAgent
from app.workflows.review_workflow import review_workflow
from app.config import settings
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Code Reviewer Agent that helps developers review code for quality, security, and best practices.

Your responsibilities include:
- Analyzing code structure and complexity
- Detecting security vulnerabilities
- Checking adherence to best practices
- Providing actionable feedback
- Generating comprehensive review reports

Be thorough, constructive, and specific in your feedback."""


class CodeReviewerAgent(BaseADKAgent):
    """Agent for code review"""

    def __init__(self):
        """Initialize Code Reviewer Agent"""
        super().__init__(
            agent_name="code_reviewer",
            system_prompt=SYSTEM_PROMPT,
            tools=[],
        )

    async def review_code(self, code: str) -> Dict[str, Any]:
        """Review code using LangGraph workflow"""
        try:
            # Execute workflow
            result = await review_workflow.ainvoke(
                {
                    "code": code,
                    "static_analysis_result": [],
                    "security_scan_result": [],
                    "best_practices_result": [],
                    "final_report": "",
                    "errors": [],
                }
            )

            # Store review in database
            self.supabase.table("code_reviews").insert(
                {
                    "review_id": f"review-{hash(code)}",
                    "code_hash": str(hash(code)),
                    "review_type": "full",
                    "review_result": result,
                    "status": "completed",
                    "workflow_state": result,
                }
            ).execute()

            return result

        except Exception as e:
            logger.error(f"Error reviewing code: {e}", exc_info=True)
            raise

