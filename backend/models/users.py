from datetime import date
from typing import Optional
import hashlib

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, relationship, mapped_column

from backend.models.base import Base,BaseType

class User(Base):
    __tablename__ = "User"
    id:Mapped[BaseType.int_primary_key]
    password:Mapped[BaseType.str_60]
    name:Mapped[BaseType.str_30]
    age:Mapped[int]
    avatar:Mapped[BaseType.optional_str_100]
    birthday:Mapped[date] = mapped_column(Date)
    email:Mapped[BaseType.str_50]
    create_time:Mapped[BaseType.update_time]

    items:Mapped[list["Item"]] \
        = relationship("Item", 
            back_populates="user", 
            cascade="all, delete-orphan", 
            lazy="select", 
            order_by="Item.name"
        )
    
    def __init__(self, password:str, name:str, age:int, avatar:Optional[str], birthday:date, email:str) -> None:
        self.password = password
        self.name = name
        self.age = age
        self.avatar = avatar
        self.birthday = birthday
        self.email = email

    # 通常用來顯示簡單資訊給使用者；有__str__時會優先__repr__顯示
    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

    # Debug、詳細顯示資訊使用
    def __repr__(self) -> str:
        return f"User(id={self.id}, password={self.password}, name={self.name}, age={self.age}, avatar={self.avatar}, birthday={self.birthday}, email={self.email})"