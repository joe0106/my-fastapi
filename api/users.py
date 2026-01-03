from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from auth.passwd import get_password_hash
from schemas import users as UserSchema
from api.depends import check_user_id, pagination_parms
#from api.depends import test_verify_token
from crud.users import UserCrudManager

router = APIRouter(
    tags=["users"],
    prefix="/api"
    # depend on header
    #,dependencies=[Depends(test_verify_token)]
)

UserCrud = UserCrudManager()

@router.get("/users", 
         response_model=List[UserSchema.UserRead],
         response_description="Get list of all users")
async def get_users(page_params:dict=Depends(pagination_parms)):
    """
    Create an user list with all the information:

    - **id**
    - **name**
    - **email**
    - **avatar**

    """
    users = await UserCrud.get_users(**page_params)
    return users

@router.get("/users/{user_id}", response_model=UserSchema.UserRead)
async def get_user_by_id(user_id: int):
    user = await UserCrud.get_user_by_id(user_id)
    if user:
        return user
    
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users", 
          response_model=UserSchema.UserCreateResponse,
          status_code=status.HTTP_201_CREATED)
async def create_users(newUser: UserSchema.UserCreate):
    user_id = await UserCrud.get_user_id_by_email(newUser.email)
    if user_id:
        raise HTTPException(status_code=409, detail="User already exists")

    # hash pwd
    newUser.password = get_password_hash(newUser.password)

    user = await UserCrud.create_user(newUser)
    return vars(user)

@router.put("/users/{user_id}}", response_model=UserSchema.UserUpdateResponse)
async def update_user(newUser: UserSchema.UserUpdate, user_id: int = Depends(check_user_id)):
    await UserCrud.update_user(user_id, newUser)
    return newUser

@router.put("/users/{user_id}/password", response_model=UserSchema.UserUpdateResponse)
async def update_user_password(newUser: UserSchema.UserUpdate, user_id: int = Depends(check_user_id)):
    await UserCrud.update_user_password(user_id, newUser)
    return newUser

@router.delete("/users/{user_id}")
async def delete_users(user_id: int = Depends(check_user_id)):
    await UserCrud.delete_users(user_id)
    return

@router.post("/userCreate" , deprecated=True)
async def create_user_deprecated(newUser: UserSchema.UserCreate):
    return "deprecated"