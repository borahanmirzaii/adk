"""Task definitions for RQ worker"""

from app.tasks.agent_tasks import execute_agent_task, process_long_running_agent_task

__all__ = [
    "execute_agent_task",
    "process_long_running_agent_task",
]


def get_task_function(task_name: str):
    """Get task function by name"""
    task_map = {
        "execute_agent_task": execute_agent_task,
        "process_long_running_agent_task": process_long_running_agent_task,
    }
    return task_map.get(task_name)

