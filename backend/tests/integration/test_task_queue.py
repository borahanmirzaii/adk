"""Integration tests for RQ task queue"""

import pytest
from unittest.mock import Mock, patch
from app.services.task_service import TaskService


class TestTaskQueue:
    """Integration tests for task queue"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        redis_mock = Mock()
        return redis_mock

    @pytest.fixture
    def mock_queue(self):
        """Mock RQ Queue"""
        queue_mock = Mock()
        job_mock = Mock()
        job_mock.id = "test-job-123"
        queue_mock.enqueue.return_value = job_mock
        return queue_mock

    @pytest.fixture
    def task_service(self, mock_redis, mock_queue):
        """Create TaskService with mocked dependencies"""
        with patch('app.services.task_service.Redis', return_value=mock_redis), \
             patch('app.services.task_service.Queue', return_value=mock_queue):
            service = TaskService()
            service.redis_conn = mock_redis
            service.queue = mock_queue
            service.enabled = True
            return service

    def test_enqueue_task(self, task_service, mock_queue):
        """Test enqueueing a task"""
        task_id = task_service.enqueue_task(
            "execute_agent_task",
            agent_name="test_agent",
            message="test message",
            session_id="test-session"
        )
        
        assert task_id == "test-job-123"
        mock_queue.enqueue.assert_called_once()

    def test_get_task_status(self, task_service, mock_redis):
        """Test getting task status"""
        from rq.job import Job
        from datetime import datetime
        
        job_mock = Mock(spec=Job)
        job_mock.get_status.return_value = "finished"
        job_mock.created_at = datetime.now()
        job_mock.started_at = datetime.now()
        job_mock.ended_at = datetime.now()
        job_mock.result = {"status": "completed"}
        job_mock.exc_info = None
        
        with patch('app.services.task_service.Job.fetch', return_value=job_mock):
            status = task_service.get_task_status("test-job-123")
            
            assert status is not None
            assert status["task_id"] == "test-job-123"
            assert status["status"] == "finished"
            assert "result" in status

    def test_cancel_task(self, task_service, mock_redis):
        """Test cancelling a task"""
        from rq.job import Job
        
        job_mock = Mock(spec=Job)
        job_mock.cancel = Mock()
        
        with patch('app.services.task_service.Job.fetch', return_value=job_mock):
            result = task_service.cancel_task("test-job-123")
            
            assert result is True
            job_mock.cancel.assert_called_once()

    def test_enqueue_task_disabled(self):
        """Test enqueueing when task queue is disabled"""
        service = TaskService()
        service.enabled = False
        
        task_id = service.enqueue_task("test_task")
        assert task_id is None

