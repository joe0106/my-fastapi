from typing import List
from fastapi import APIRouter, Depends, HTTPException

from api.depends import check_item_id
from auth.utils import get_current_user
from crud.items import ItemCrudManager
from schemas import items as ItemSchema
from schemas import users as UserSchema
from database.fake_db import get_db

router = APIRouter(
    tags=["items"],
    prefix="/api"
)
fake_db = get_db()

Exception403 = HTTPException(status_code=403, detail="Forbidden")

ItemCrud = ItemCrudManager()

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
async def delete_items(
    deleteItem: ItemSchema.CurrentItem = Depends(check_item_id),
    user: UserSchema.CurrentUser = Depends(get_current_user)):
    if not deleteItem or deleteItem.user_id != user.id:
        raise Exception403
    
    await ItemCrud.delete_item_by_id(deleteItem.id)

@router.put("/items/{item_id}", response_model=ItemSchema.ItemUpdate)
async def update_item(
    newItem: ItemSchema.ItemUpdate,
    item: ItemSchema.CurrentItem = Depends(check_item_id),
    user: UserSchema.CurrentUser = Depends(get_current_user)):
    if user.id != item.user_id:
        raise Exception403
    
    item = await ItemCrud.update_item_by_id(item.id, newItem)
    return item