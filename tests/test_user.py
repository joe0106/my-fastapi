
from functools import lru_cache
import json
import random
import pytest

from tests.conftest import async_client

@lru_cache()
def get_user_data():
    with open("./tests/data/user_data.json") as f:
        data = json.load(f)
    return data

def get_random_user():
    return [ random.choice(get_user_data()) ]

@pytest.mark.parametrize("user", get_user_data())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(async_client, user):
    response = await async_client.post("/api/users", json=user)
    
    assert response.status_code == 201
    assert response.json()["name"] == user["name"]
    assert response.json()["email"] == user["email"]
    assert "id" in response.json()
    assert isinstance(response.json()["id"], int)

# @pytest.mark.parametrize("user", get_random_user())
# async def test_create_duplicate_user(async_client, user):

# test_create_invalid_email_user
# test_create_invalid_password_user
# test_create_invalid_age_user
# test_create_invalid_birthday_user
# test_create_invalid_name_user

@pytest.mark.asyncio(loop_scope="session")
async def test_get_users(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == { "name", "id", "email", "avatar" }