from datetime import datetime
from sqlalchemy import ARRAY, Column, Integer
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    username: str = Field(min_length=3, max_length=100, unique=True)
    email: EmailStr = Field(unique=True)
    role: str = Field(default="user")

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    refresh_token: Optional[str] = None
    hashed_password: str
    created_at: datetime
    order_ids: Optional[list[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    
    order: Optional[list["Order"]] = Relationship(back_populates="user", cascade_delete=True) # type: ignore
 
class UserCreate(UserBase):
    password: str   

class UserRead(UserBase):
    id: int
