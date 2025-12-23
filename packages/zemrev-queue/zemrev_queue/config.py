"""
============================================================================
FILE: packages/zemrev-queue/zemrev_queue/config.py
PURPOSE: Shared queue configuration (reusable across all services)
============================================================================
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class QueueConfig(BaseSettings):
    """Queue configuration (read from environment)"""
    
    # Redis connection
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    
    # Queue settings
    QUEUE_NAME: str = "zemrev_jobs"
    QUEUE_MAX_RETRIES: int = 3
    QUEUE_JOB_TIMEOUT: int = 600  # 10 minutes
    QUEUE_RESULT_TTL: int = 300   # 5 minutes
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

# Global config instance
config = QueueConfig()