import pytest_asyncio
import pytest
import os
import redis.asyncio as redis
from functools import lru_cache

redis_connection = None

@pytest_asyncio.fixture(autouse=True)
async def setup_redis(dependencies):
    """自動初始化 Redis 連線"""
    global redis_connection
    # 使用 redis.from_url 建立非同步連線
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_connection = redis.Redis.from_url(redis_url)
    
    yield redis_connection
    
    if redis_connection:
        await redis_connection.close()

@pytest.mark.redis_con_test
@pytest.mark.asyncio
async def test_redis_connection():
    value = 'bar_async'
    await redis_connection.set('foo_async', value)
    result = await redis_connection.get('foo_async')
    assert result.decode() == value

@pytest.mark.redis_con_test
@pytest.mark.asyncio
async def test_redis_connection_pool():
    value = 'bar2_async'
    await redis_connection.set('foo2_async', value)
    result = await redis_connection.get('foo2_async')
    assert result.decode() == value
