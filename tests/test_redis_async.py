import pytest
import redis.asyncio as redis

REDIS_URL = "redis://localhost:6379"
CONNECTION_POOL = redis.ConnectionPool.from_url(REDIS_URL)

@pytest.mark.redis_con_test
@pytest.mark.asyncio
async def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)
    value = 'bar_async'
    await redis_connection.set('foo_async', value)
    result = await redis_connection.get('foo_async')
    redis_connection.close()
    assert result.decode() == value

@pytest.mark.redis_con_test
@pytest.mark.asyncio
async def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=CONNECTION_POOL)

    value = 'bar2_async'
    await redis_connection.set('foo2_async', value)
    result = await redis_connection.get('foo2_async')
    redis_connection.close()

    assert result.decode() == value