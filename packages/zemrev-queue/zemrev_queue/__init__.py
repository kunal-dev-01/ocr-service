"""
============================================================================
FILE: packages/zemrev-queue/zemrev_queue/__init__.py
PURPOSE: Package exports
============================================================================
"""

from .config import QueueConfig, config
from .redis_client import RedisClient, redis_client
from .queue_manager import QueueManager, queue_manager, JobStatus

__all__ = [
    # Config
    "QueueConfig",
    "config",
    # Redis Client
    "RedisClient",
    "redis_client",
    # Queue Manager
    "QueueManager",
    "queue_manager",
    "JobStatus",
]

__version__ = "1.0.0"