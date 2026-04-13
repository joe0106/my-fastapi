import redis
import pytest

REDIS_URL = "redis://localhost:6379"
CONNECTION_POOL = redis.ConnectionPool.from_url(REDIS_URL)

# 2 ways to connect redis
@pytest.mark.redis_con_test
def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)

    value = 'bar'
    redis_connection.set('foo', value)
    result = redis_connection.get('foo')
    redis_connection.close()

    assert result.decode() == value

@pytest.mark.redis_con_test
def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=CONNECTION_POOL)

    value = 'bar2'
    redis_connection.set('foo2', value)
    result = redis_connection.get('foo2')
    redis_connection.close()

    assert result.decode() == value