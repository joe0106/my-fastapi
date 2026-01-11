from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    name: str
    # model_config = {
    #     "from_attributes": True
    # }

class UserCreate(UserBase):
    password: str = Field(min_length=6)
    name: str = Field(min_length=3)
    avatar: Optional[str] = Field(min_length=3)
    age: int = Field(gt=0, lt=100)
    email: str = Field()
    birthday: date = Field()

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "password": "123456",
                    "name": "user1",
                    "avatar": "https://i.imgur.com/4M34hi2.png",
                    "age": 18,
                    "email": "user1@email.com",
                    "birthday": "2003-01-01"
                }
            ]
        }
    }

class UserRead(UserBase):
    id: str
    email: str
    avatar: Optional[str] = None

class UserCreateResponse(UserBase):
    id: int
    email: str

class UserUpdate(UserBase):
    #password: Optional[str] = Field(min_length=6)
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0, lt=100)
    birthday: Optional[date] = Field()

class UserUpdatePassword(UserBase):
    password: str

class UserUpdateResponse(UserBase):
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0, lt=100)
    birthday: Optional[date] = Field()

class UserInDB(BaseModel):
    id: int
    name: str
    password: str

class CurrentUser(BaseModel):
    id: int
    name: str
    email: str