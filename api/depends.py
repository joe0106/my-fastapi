from typing import Optional
from fastapi import HTTPException
from fastapi.params import Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.generic import get_db
from models.users import User as UserModel


def check_user_id(user_id: int):
    '''
    查詢使用者是否存在的Depends
    
    :param user_id: Description
    :type user_id: int
    '''
    db_session:Session = get_db()
    stmt = select(UserModel).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

def pagination_parms(keyword:Optional[str]=None, last:int=0, limit:int=50):
    return {
        "keyword": keyword,
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