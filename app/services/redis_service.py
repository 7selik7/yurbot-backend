from typing import Optional
from redis.asyncio import ConnectionPool, Redis
from app.core.config import settings


class RedisPool:
    def __init__(self) -> None:
        self._pool: Optional[ConnectionPool] = None
        self._redis: Optional[Redis] = None

    async def init_pool(self) -> None:
        if not self._pool:
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            self._redis = Redis(connection_pool=self._pool)

    async def get_redis(self) -> Redis:
        if not self._redis:
            await self.init_pool()
        return self._redis

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
        if self._pool:
            await self._pool.disconnect()
        self._redis = None
        self._pool = None

    async def remove_keys_by_pattern(self, pattern: str) -> None:
        redis = await self.get_redis()
        keys = []
        async for key in redis.scan_iter(pattern):
            keys.append(key)
        if keys:
            await redis.delete(*keys)


redis_pool = RedisPool()