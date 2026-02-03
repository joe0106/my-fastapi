
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

@lru_cache()
def get_dup_user_data():
    with open("./tests/data/duplicate_user.json") as f:
        data = json.load(f)
    return data

@pytest.mark.parametrize("user", get_user_data())
@pytest.mark.asyncio(loop_scope="module")
async def test_create_user(async_client, user):
    response = await async_client.post("/api/users", json=user)
    
    assert response.status_code == 201
    assert response.json()["name"] == user["name"]
    assert response.json()["email"] == user["email"]
    assert "id" in response.json()
    assert isinstance(response.json()["id"], int)

@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_dup_user_data())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_duplicate_user(async_client, user):
    response1 = await async_client.post("/api/users", json=user)
    assert response1.status_code == 201
    response2 = await async_client.post("/api/users", json=user)
    assert response2.status_code == 409
    
@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_random_user())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_invalid_email_user(async_client, user):
    invalid_email_user = user.copy()
    invalid_email_user["email"] = "bad@email@mal.coom"
    response = await async_client.post("/api/users", json=invalid_email_user)
    assert response.status_code == 422
    
@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_random_user())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_invalid_password_user(async_client, user):
    invalid_pwd_user = user.copy()
    invalid_pwd_user["password"] = '1'
    response = await async_client.post("/api/users", json=invalid_pwd_user)
    assert response.status_code == 422

@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_random_user())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_invalid_age_user(async_client, user):
    invalid_age_user = user.copy()
    invalid_age_user["age"] = 123
    invalid_age_user["email"] = '111@mail.com'
    response = await async_client.post("/api/users", json=invalid_age_user)
    assert response.status_code == 422

@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_random_user())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_invalid_birthday_user(async_client, user):
    invalid_bday_user = user.copy()
    invalid_bday_user["birthday"] = 123
    invalid_bday_user["email"] = '222@mail.com'
    response = await async_client.post("/api/users", json=invalid_bday_user)
    assert response.status_code == 422

@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.parametrize("user", get_random_user())
@pytest.mark.asyncio(loop_scope="session")
async def test_create_invalid_name_user(async_client, user):
    invalid_name_user = user.copy()
    invalid_name_user["name"] = 123
    response = await async_client.post("/api/users", json=invalid_name_user)
    assert response.status_code == 422

@pytest.mark.skip(reason="Temporarily disabled for demonstration purposes")
@pytest.mark.asyncio(loop_scope="session")
async def test_get_users(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert set(response.json()[0].keys()) == { "name", "id", "email", "avatar" }