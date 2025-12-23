"""
============================================================================
FILE: packages/zemrev-queue/zemrev_queue/redis_client.py
PURPOSE: Shared Redis client
============================================================================
"""

import redis.asyncio as aioredis
from .config import config
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Async Redis client - connects to shared queue"""
    
    def __init__(self):
        self.redis = None
        self.pool = None
    
    async def connect(self):
        """Connect to shared Redis queue"""
        try:
            self.pool = aioredis.ConnectionPool.from_url(
                config.REDIS_URL,
                max_connections=config.REDIS_MAX_CONNECTIONS,
                socket_timeout=config.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=5,
                decode_responses=True,
                encoding="utf-8"
            )
            
            self.redis = aioredis.Redis(connection_pool=self.pool)
            await self.redis.ping()
            
            logger.info(f"✅ Redis connected: {config.REDIS_URL}")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close connection"""
        if self.redis:
            await self.redis.aclose()
        if self.pool:
            await self.pool.aclose()
        logger.info("Redis disconnected")
    
    async def ping(self) -> bool:
        """Health check"""
        try:
            return await self.redis.ping()
        except:
            return False
    
    # Basic operations
    async def get(self, key: str):
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        return await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        return await self.redis.delete(key)
    
    async def incr(self, key: str):
        return await self.redis.incr(key)
    
    async def ttl(self, key: str):
        return await self.redis.ttl(key)
    
    # Queue operations
    async def lpush(self, key: str, *values):
        return await self.redis.lpush(key, *values)
    
    async def rpop(self, key: str):
        return await self.redis.rpop(key)
    
    async def llen(self, key: str):
        return await self.redis.llen(key)
    
    async def exists(self, key: str):
        return await self.redis.exists(key)

# Global instance
redis_client = RedisClient()