"""Tools for Infrastructure Monitor Agent"""

from typing import Dict, Any, List
import docker
import psutil
import logging

logger = logging.getLogger(__name__)


def check_docker_containers() -> Dict[str, Any]:
    """Check status of Docker containers"""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        result = {
            "total": len(containers),
            "running": len([c for c in containers if c.status == "running"]),
            "stopped": len([c for c in containers if c.status == "exited"]),
            "containers": [
                {
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown",
                }
                for c in containers
            ],
        }
        return result
    except Exception as e:
        logger.error(f"Error checking Docker containers: {e}")
        return {"error": str(e)}


def check_disk_space() -> Dict[str, Any]:
    """Check disk space usage"""
    try:
        disk = psutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": round((disk.used / disk.total) * 100, 2),
        }
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return {"error": str(e)}


def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage"""
    try:
        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "percent_used": round(memory.percent, 2),
        }
    except Exception as e:
        logger.error(f"Error checking memory usage: {e}")
        return {"error": str(e)}


def check_database_connection() -> Dict[str, Any]:
    """Check database connection (placeholder)"""
    # TODO: Implement actual database connection check
    return {
        "status": "unknown",
        "message": "Database connection check not yet implemented",
    }

