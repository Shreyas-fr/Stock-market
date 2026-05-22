import redis.asyncio as aioredis
import json
from typing import Any, Optional
from app.config import settings
from loguru import logger


class RedisService:
    _client: Optional[aioredis.Redis] = None

    @classmethod
    async def connect(cls):
        cls._client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        await cls._client.ping()
        logger.info("Redis connected")

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.aclose()

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        value = await cls._client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = 3600):
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await cls._client.setex(key, ttl, serialized)

    @classmethod
    async def delete(cls, key: str):
        await cls._client.delete(key)

    @classmethod
    async def publish(cls, channel: str, message: Any):
        payload = json.dumps(message) if not isinstance(message, str) else message
        await cls._client.publish(channel, payload)

    @classmethod
    async def get_client(cls) -> aioredis.Redis:
        return cls._client


redis_service = RedisService()


async def get_redis():
    return redis_service
