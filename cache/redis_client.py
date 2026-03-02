from redis.asyncio import Redis, from_url
from config.settings import settings

redis_client = from_url(settings.redis_url, decode_responses=True)

async def get_redis() -> Redis:
    return redis_client
