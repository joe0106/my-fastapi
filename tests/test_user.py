
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

#Create
@pytest.mark.parametrize("user", get_user_data())
@pytest.mark.asyncio(loop_scope="module")
async def test_create_user(async_client, user):
    response = await async_client.post("/api/users", json=user)
    
    assert response.status_code == 201
    assert response.json()["name"] == user["name"]
    assert response.json()["email"] == user["email"]
    assert "id" in response.json()
    assert isinstance(response.json()["id"], int)

@pytest.mark.asyncio(loop_scope="module")
async def test_create_duplicate_user(async_client, single_user_data):
    user = single_user_data.copy()
    response1 = await async_client.post("/api/users", json=user)
    assert response1.status_code == 201
    response2 = await async_client.post("/api/users", json=user)
    assert response2.status_code == 409
    
@pytest.mark.asyncio(loop_scope="module")
async def test_create_invalid_email_user(async_client, single_user_data):
    invalid_email_user = single_user_data.copy()
    invalid_email_user["email"] = "bad@email@mal.coom"
    response = await async_client.post("/api/users", json=invalid_email_user)
    assert response.status_code == 422
    
@pytest.mark.asyncio(loop_scope="module")
async def test_create_invalid_password_user(async_client, single_user_data):
    invalid_pwd_user = single_user_data.copy()
    invalid_pwd_user["password"] = '1'
    response = await async_client.post("/api/users", json=invalid_pwd_user)
    assert response.status_code == 422

@pytest.mark.asyncio(loop_scope="module")
async def test_create_invalid_age_user(async_client, single_user_data):
    invalid_age_user = single_user_data.copy()
    invalid_age_user["age"] = 123
    invalid_age_user["email"] = '111@mail.com'
    response = await async_client.post("/api/users", json=invalid_age_user)
    assert response.status_code == 422

@pytest.mark.asyncio(loop_scope="module")
async def test_create_invalid_birthday_user(async_client, single_user_data):
    invalid_bday_user = single_user_data.copy()
    invalid_bday_user["birthday"] = 123
    invalid_bday_user["email"] = '222@mail.com'
    response = await async_client.post("/api/users", json=invalid_bday_user)
    assert response.status_code == 422

@pytest.mark.asyncio(loop_scope="module")
async def test_create_invalid_name_user(async_client, single_user_data):
    invalid_name_user = single_user_data.copy()
    invalid_name_user["name"] = 123
    response = await async_client.post("/api/users", json=invalid_name_user)
    assert response.status_code == 422

@pytest.mark.asyncio(loop_scope="module")
async def test_get_users(async_client, single_user_data):
    user = single_user_data.copy()
    insert_user_result = await async_client.post("/api/users", json=user)
    response = await async_client.get("/api/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
    user = response.json()[0]
    assert set(user.keys()) == { "name", "id", "email", "avatar" }

#Read
async def get_user_id(async_client, user):
    user = user.copy()
    response = await async_client.get(f'/api/users?keyword={user["name"]}&last=0&limit=50')
    return response.json()[0]["id"]

@pytest.mark.asyncio(loop_scope="module")
async def test_get_user_by_id(async_client, single_user_data):
    #先keyword取得user_id
    user_id = await get_user_id(async_client, single_user_data)
    response = await async_client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio(loop_scope="module")
async def test_get_user_not_found(async_client):
    response = await async_client.get(f"/api/users/0")
    assert response.status_code == 404

@pytest.mark.asyncio(loop_scope="module")
async def test_get_user_by_keyword(async_client, single_user_data):
    user = single_user_data.copy()
    response = await async_client.get(f'/api/users?keyword={user["name"]}&last=0&limit=50')
    assert response.status_code == 200
    assert len(response.json()) > 0

#Update
async def get_access_token(async_client, user):
    #do login
    payload = {
        "grant_type" : "",
        "username" : user["email"],
        "password" : user["password"],
        "scopes" : "",
        "client_id" : "",
        "client_secret" : ""
    }
    response = await async_client.post(f"/api/auth/login", data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]
    return access_token

@pytest.mark.asyncio(loop_scope="module")
async def test_update_user(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    #get user token
    user_access_token = await get_access_token(async_client, single_user_data)
    payload = single_user_data.copy()
    payload["name"] += " Updated"
    payload["avatar"] = "https://fake_url.com/fake.img"
    payload["age"] = 25
    response = await async_client.put(f"/api/users/{user_id}", json=payload, headers={"Authorization": f"Bearer {user_access_token}"})
    assert response.status_code == 200

@pytest.mark.asyncio(loop_scope="module")
async def test_update_user_unauthorized(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    payload = single_user_data.copy()
    response = await async_client.put(f"/api/users/{user_id}", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio(loop_scope="module")
async def test_update_invalid_schema(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    #get user token
    user_access_token = await get_access_token(async_client, single_user_data)
    payload = single_user_data.copy()
    payload["age"] = -1
    response = await async_client.put(f"/api/users/{user_id}", json=payload, headers={"Authorization": f"Bearer {user_access_token}"})
    assert response.status_code == 422

@pytest.mark.asyncio(loop_scope="module")
async def test_update_user_password(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    #get user token
    user_access_token = await get_access_token(async_client, single_user_data)
    new_password = '234567'
    payload = {
        "password": new_password
    }
    response = await async_client.put(f"/api/users/{user_id}/password", json=payload, headers={"Authorization": f"Bearer {user_access_token}"})
    assert response.status_code == 204

    #get access token again
    new_user_data = single_user_data.copy()
    new_user_data["password"] = new_password
    new_access_token = await get_access_token(async_client, new_user_data)
    assert new_access_token

@pytest.mark.asyncio(loop_scope="module")
async def test_update_user_password_unauthorized(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    
    new_password = '234567'
    payload = {
        "password": new_password
    }
    response = await async_client.put(f"/api/users/{user_id}/password", json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio(loop_scope="module")
async def test_delete_user(async_client, single_user_data):
    user_data = single_user_data.copy()
    user_data["password"] = '234567'
    #get user id
    user_id = await get_user_id(async_client, user_data)
    user_access_token = await get_access_token(async_client, user_data)
    response = await async_client.delete(f'/api/users/{user_id}', headers={"Authorization": f"Bearer {user_access_token}"})
    assert response.status_code == 204

    user = single_user_data.copy()
    await async_client.post("/api/users", json=user)

@pytest.mark.asyncio(loop_scope="module")
async def test_delete_user_unauthorized(async_client, single_user_data):
    #get user id
    user_id = await get_user_id(async_client, single_user_data)
    response = await async_client.delete(f'/api/users/{user_id}')
    assert response.status_code == 401