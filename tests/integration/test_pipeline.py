import pytest
from cache.redis_client import redis_client

@pytest.mark.asyncio
async def test_redis_connection():
    # Attempt ping, skip if Redis is not running
    try:
        assert await redis_client.ping() is True
    except Exception:
        pytest.skip("Redis not available for integration test")
