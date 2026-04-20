import redis
import pytest
import os

redis_connection = None

@pytest.fixture(autouse=True)
def setup_redis(dependencies):
    """自動初始化 Redis 連線"""
    global redis_connection
    # 使用 redis.from_url 建立連線
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_connection = redis.Redis.from_url(redis_url)

    yield redis_connection

    if redis_connection:
        redis_connection.close()

# 2 ways to connect redis
@pytest.mark.redis_con_test
def test_redis_connection():
    value = 'bar'
    redis_connection.set('foo', value)
    result = redis_connection.get('foo')
    redis_connection.close()

    assert result.decode() == value

@pytest.mark.redis_con_test
def test_redis_connection_pool():
    value = 'bar2'
    redis_connection.set('foo2', value)
    result = redis_connection.get('foo2')
    redis_connection.close()

    assert result.decode() == value