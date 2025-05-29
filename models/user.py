from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field
from typing import List, Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)
    role: str = Field(default="user")

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    refresh_token: Optional[str] = None
    hashed_password: str
    created_at: datetime
    
    todolist: List["TodoList"] | None = Relationship(back_populates="user", cascade_delete=True) # type: ignore

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
