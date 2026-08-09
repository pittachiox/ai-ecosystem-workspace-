from __future__ import annotations

from arq import create_pool
from arq.connections import RedisSettings

from app.core.config import settings


class RedisService:
    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url or settings.redis_url
        self.redis_settings = RedisSettings.from_dsn(self.redis_url)

    async def get_pool(self):
        return await create_pool(self.redis_settings)

    async def enqueue(self, function_name: str, *args, **kwargs):
        redis = await create_pool(self.redis_settings)
        try:
            return await redis.enqueue_job(function_name, *args, **kwargs)
        finally:
            await redis.close()


redis_service = RedisService()
