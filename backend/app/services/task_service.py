"""RQ task queue service for async processing"""

from typing import Optional, Dict, Any
import logging
from redis import Redis
from rq import Queue, Job
from rq.job import JobStatus
from app.config import settings
from app.dependencies import get_redis_client

logger = logging.getLogger(__name__)


class TaskService:
    """Service for managing async tasks with RQ"""

    def __init__(self):
        """Initialize task service"""
        try:
            # Get Redis connection for RQ
            redis_client = get_redis_client()
            # RQ uses sync Redis, so we need a separate connection
            self.redis_conn = Redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB + 1  # Use different DB for RQ
            )
            self.queue = Queue('default', connection=self.redis_conn)
            self.enabled = True
            logger.info("RQ task queue initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RQ: {e}")
            self.enabled = False
            self.queue = None
            self.redis_conn = None

    def enqueue_task(
        self, task_name: str, *args, **kwargs
    ) -> Optional[str]:
        """
        Enqueue a task for async processing
        
        Args:
            task_name: Name of the task function to execute
            *args: Positional arguments for the task
            **kwargs: Keyword arguments for the task
        
        Returns:
            Task ID if successful, None otherwise
        """
        if not self.enabled or not self.queue:
            logger.warning("Task queue not enabled, task not queued")
            return None

        try:
            # Import task function dynamically
            from app.tasks import get_task_function
            task_func = get_task_function(task_name)
            
            if not task_func:
                logger.error(f"Task function {task_name} not found")
                return None
            
            # Enqueue the task
            job = self.queue.enqueue(
                task_func,
                *args,
                **kwargs,
                job_timeout='10m',  # 10 minute timeout
                result_ttl=3600,  # Keep results for 1 hour
                failure_ttl=86400,  # Keep failures for 24 hours
            )
            
            logger.info(f"Task {task_name} enqueued with ID {job.id}")
            return job.id
        except Exception as e:
            logger.error(f"Error enqueueing task {task_name}: {e}")
            return None

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a task
        
        Args:
            task_id: Task ID returned from enqueue_task
        
        Returns:
            Dictionary with task status information
        """
        if not self.enabled or not self.redis_conn:
            return None

        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            
            status_info = {
                "task_id": task_id,
                "status": job.get_status(),
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            }
            
            # Add result if completed
            if job.get_status() == JobStatus.FINISHED:
                status_info["result"] = job.result
            elif job.get_status() == JobStatus.FAILED:
                status_info["error"] = str(job.exc_info) if job.exc_info else "Unknown error"
            
            return status_info
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {e}")
            return None

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task
        
        Args:
            task_id: Task ID to cancel
        
        Returns:
            True if cancelled successfully, False otherwise
        """
        if not self.enabled or not self.redis_conn:
            return False

        try:
            job = Job.fetch(task_id, connection=self.redis_conn)
            job.cancel()
            logger.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False


# Global task service instance
task_service = TaskService()

