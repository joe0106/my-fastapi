from typing import List
from fastapi import APIRouter, HTTPException

from schemas import items as ItemSchema
from database.fake_db import get_db

router = APIRouter(
    tags=["items"],
    prefix=["/api"]
)
fake_db = get_db()

@router.get("/items", response_model=List[ItemSchema.ItemRead])
def get_items(query: str = None):
    return fake_db["items"]

@router.get("/items/{item_id}", response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id: int, query: str = None):
    for item in fake_db["items"]:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/items", response_model=ItemSchema.ItemCreate)
def create_item(newItem: ItemSchema.ItemCreate):
    for item in fake_db["items"]:
        if newItem.id == item["id"]:
            raise HTTPException(status_code=409, detail="Item already exist")
    fake_db["items"].append(newItem.model_dump())
    return newItem

@router.delete("/items/{item_id}")
def delete_items(item_id: int):
    for item in fake_db["item"]:
        if item["id"] == item_id:
            fake_db["item"].remove(item_id)
            return item
    raise HTTPException(status_code=404, detail="Item not found")