from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional

class TodoBase(SQLModel):
    title: str
    description: Optional[str]

class TodoList(TodoBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime
    
    user_id: int = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="todolist") # type: ignore

    task: Optional["Task"] = Relationship(back_populates="todolist", cascade_delete=True) # type: ignore

class TodoCreate(TodoBase):
    user_name: str = Field(..., min_length=3, max_length=100, description="User name cant be empty")

class TodoRead(TodoBase):
    id: int
