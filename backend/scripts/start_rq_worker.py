#!/usr/bin/env python3
"""Start RQ worker for processing async tasks"""

import os
import sys
import logging
from rq import Worker, Queue, Connection
from redis import Redis
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start RQ worker"""
    try:
        # Connect to Redis
        redis_conn = Redis.from_url(
            settings.REDIS_URL,
            db=settings.REDIS_DB + 1  # Use different DB for RQ
        )
        
        # Create queue
        queue = Queue('default', connection=redis_conn)
        
        logger.info("Starting RQ worker...")
        logger.info(f"Redis URL: {settings.REDIS_URL}")
        logger.info(f"Queue: default")
        
        # Start worker
        with Connection(redis_conn):
            worker = Worker([queue])
            worker.work()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

