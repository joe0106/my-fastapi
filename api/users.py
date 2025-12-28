from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete


from schemas import users as UserSchema
from database.generic import get_db
from models.users import User as UserModel

router = APIRouter(
    tags=["users"],
    prefix="/api"
)

fake_db = get_db()

@router.get("/users", 
         response_model=List[UserSchema.UserRead],
         response_description="Get list of all users")
def get_users(query: str = None):
    """
    Create an user list with all the information:

    - **id**
    - **name**
    - **email**
    - **avatar**

    """
    db_session = get_db()
    stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar)
    users = db_session.execute(stmt).all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema.UserRead)
def get_user_by_id(user_id: int, query: str = None):
    db_session:Session = get_db()
    stmt = select(UserModel).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", 
          response_model=UserSchema.UserCreateResponse,
          status_code=status.HTTP_201_CREATED)
def create_users(newUser: UserSchema.UserCreate):
    db_session:Session = get_db()

    # query using session.query()
    #user = db_session.query(UserModel).filter(UserModel.email == newUser.email).first()
    # query using session.execute() a statement
    stmt = select(UserModel.id).where(UserModel.email == newUser.email)
    user = db_session.execute(stmt).first()
    # raise ex if user exist
    if user:
        raise HTTPException(status_code=409, detail="User already exists")

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

@router.post("/userCreate" , deprecated=True)
def create_user_deprecated(newUser: UserSchema.UserCreate):
    return "deprecated"

@router.put("/users/{user_id}}", response_model=UserSchema.UserUpdateResponse)
def update_user(user_id: int, newUser: UserSchema.UserUpdate):
    db_session = get_db()

    stmt = select(UserModel).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        name = newUser.Name,
        password = newUser.password,
        age = newUser.age,
        birthday = newUser.birthday,
        avatar = newUser.avatar
    )
    db_session.execute(stmt)
    db_session.commit()

    return newUser

@router.put("/users/{user_id}/password", response_model=UserSchema.UserUpdateResponse)
def update_user_password(user_id: int, newUser: UserSchema.UserUpdate):
    db_session = get_db()
    stmt = select(UserModel).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        password = newUser.password
    )
    db_session.execute(stmt)
    db_session.commit()

    return newUser

@router.delete("/users/{user_id}")
def delete_users(user_id: int):
    db_session = get_db()

    stmt = select(UserModel).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return