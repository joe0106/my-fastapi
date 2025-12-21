from typing import List
from fastapi import FastAPI, HTTPException
from setting.config import get_settings

from schemas import users as UserSchema
from schemas import items as ItemSchema
from database.fake_db import get_db

app = FastAPI()

fake_db = get_db()

@app.get("/")
def hello_world():
    return "hello world !!! @@"

#Users
@app.get("/users", response_model=List[UserSchema.UserRead])
def get_users(query: str = None):
    return fake_db["users"]

@app.get("/users/{user_id}", response_model=UserSchema.UserRead)
def get_user_by_id(user_id: int, query: str = None):
    for user in fake_db["users"]:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", response_model=UserSchema.UserCreateResponse)
def create_users(newUser: UserSchema.UserCreate):
    for user in fake_db["users"]:
        if newUser.id == user["id"]:
            raise HTTPException(status_code=409, detail="User already exist")
    fake_db["users"].append(newUser.model_dump())
    return newUser

@app.delete("/users/{user_id}")
def delete_users(user_id: int):
    for user in fake_db["users"]:
        if user["id"] == user_id:
            fake_db["users"].remove(user)
            return f"user_id: {user["id"]} deleted"
    raise HTTPException(status_code=404, detail="User not found")

#Items
@app.get("/items", response_model=List[ItemSchema.ItemRead])
def get_items(query: str = None):
    return fake_db["items"]

@app.get("/items/{item_id}", response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id: int, query: str = None):
    for item in fake_db["items"]:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=ItemSchema.ItemCreate)
def create_item(newItem: ItemSchema.ItemCreate):
    for item in fake_db["items"]:
        if newItem.id == item["id"]:
            raise HTTPException(status_code=409, detail="Item already exist")
    fake_db["items"].append(newItem.model_dump())
    return newItem

@app.delete("/items/{item_id}")
def delete_items(item_id: int):
    for item in fake_db["item"]:
        if item["id"] == item_id:
            fake_db["item"].remove(item_id)
            return item
    raise HTTPException(status_code=404, detail="Item not found")

#Others
@app.get("/infor")
def get_infor():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode,
        "port": settings.port,
        "reload": settings.reload,
        "database_url": settings.database_url
    }