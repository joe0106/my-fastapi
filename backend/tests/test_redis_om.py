import pytest
from redis_om import JsonModel, get_redis_connection, HashModel, Field, Migrator
from typing import Optional

REDIS_URL = "redis://localhost:6379"

redis = get_redis_connection(url=REDIS_URL)

class UserHashCache(HashModel, index=True):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    avatar: Optional[str] = Field(index=False)

    class Meta:
        database = redis

class UserJsonCache(JsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    avatar: Optional[str] = Field(index=False)

    class Meta:
        database = redis

#透過Migrator建立index
Migrator().run()

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