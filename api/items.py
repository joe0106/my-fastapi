from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from api.depends import check_item_id, pagination_parms
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
Exception404 = HTTPException(status_code=404, detail="Item not found")

ItemCrud = ItemCrudManager()

@router.get("/items", 
            response_model=List[ItemSchema.ItemRead],
            response_description="Get list of all Items")
async def get_items(pageparams: dict = Depends(pagination_parms)):
    return await ItemCrud.get_items(**pageparams)

@router.get("/items/{item_id}", 
            response_model=ItemSchema.ItemRead)
async def get_item_by_id(item_id: int):
    Item = await ItemCrud.get_item_by_id(item_id)
    if Item:
        return Item
    raise Exception404

@router.post("/items", 
             response_model=ItemSchema.ItemCreateResponse,
             status_code=status.HTTP_201_CREATED)
async def create_item(
    newItem: ItemSchema.ItemCreate,
    user: UserSchema.CurrentUser = Depends(get_current_user)):
    item = await ItemCrud.create_item(newItem, user.id)
    return item

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