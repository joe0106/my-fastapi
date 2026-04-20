import pytest
import os
from redis_om import JsonModel, get_redis_connection, HashModel, Field, Migrator
from typing import Optional

redis_connection = None

@pytest.fixture(autouse=True)
def setup_redis(dependencies):
    """自動初始化 Redis 連線"""
    global redis_connection
    # 使用 redis.from_url 建立非同步連線
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_connection = get_redis_connection(url=redis_url)
    
    #"補上"redis connection
    UserHashCache.Meta.database = redis_connection
    UserJsonCache.Meta.database = redis_connection

    #透過Migrator建立index
    Migrator().run()

    yield redis_connection
    
    if redis_connection:
        redis_connection.close()

class UserHashCache(HashModel, index=True):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    avatar: Optional[str] = Field(index=False)

    class Meta:
        database = redis_connection

class UserJsonCache(JsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    avatar: Optional[str] = Field(index=False)

    class Meta:
        database = redis_connection


@pytest.mark.redis_con_test
def test_create_user_hash():
    new_user = UserHashCache(
        id=1,
        name="hash_user",
        email="hash_user@email.com",
        avatar="image_url"
    )
    new_user.save()
    pk = new_user.pk
    assert UserHashCache.get(pk) == new_user

@pytest.mark.redis_con_test
def test_find_user_hash():
    user = UserHashCache(
        id=1,
        name="hash_user",
        email="hash_user@email.com",
        avatar="image_url"
    )
    result = UserHashCache.find(UserHashCache.id == 1).first()

    assert result.id == user.id
    assert result.name == user.name