from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete
import hashlib


from database.generic import get_db
from models.users import User as UserModel 
from schemas import users as UserSchema

db_session:Session = get_db()

def get_user_id_by_email(email: str):
    stmt = select(UserModel.id).where(UserModel.email == email)
    user_id = db_session.execute(stmt).first()
    if user_id:
        return user_id
    return None

def create_user(newUser: UserSchema.UserCreate):
    user = UserModel(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        email=newUser.email,
        avatar=newUser.avatar,
        )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return vars(user)

def get_users(keyword:str = None, last:int = 0, limit:int = 50):
    stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar)
    if keyword:
        stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
    users = db_session.execute(stmt).all()
    return users