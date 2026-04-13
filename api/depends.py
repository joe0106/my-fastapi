from typing import Optional
from fastapi import HTTPException
from fastapi.params import Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.items import ItemCrudManager
from crud.users import UserCrudManager
from database.generic import get_db
from models.users import User as UserModel

UserCrud = UserCrudManager()
ItemCrud = ItemCrudManager()

async def check_user_id(user_id: int):
    '''
    查詢使用者是否存在的Depends
    
    :param user_id: Description
    :type user_id: int
    '''
    user_id = await UserCrud.get_user_id_by_id(user_id)

    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id

async def check_item_id(item_id:int):
    item = await ItemCrud.get_item_in_db_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

def pagination_parms(keyword:Optional[str]=None, email: Optional[str]=None, last:int=0, limit:int=50):
    return {
        "keyword": keyword,
        "email": email,
        "last": last,
        "limit": limit
    }

class paginationParams:
    def __init__(self, keyword:Optional[str]=None, last:int=0, limit:int=50):
        self.keyword = keyword
        self.last = last
        self.limit = limit

def test_verify_token(verify_header: str = Header()):
    if verify_header != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return verify_header