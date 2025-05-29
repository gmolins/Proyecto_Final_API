from datetime import datetime, date
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional

class TaskBase(SQLModel):
    title: str
    description: Optional[str]
    due_date: Optional[date] = None
    is_completed: bool = False

class Task(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime

    todolist_id: int = Field(default=None, foreign_key="todolist.id")
    todolist: Optional["TodoList"] = Relationship(back_populates="task") # type: ignore

    status_id: int = Field(default=None, foreign_key="status.id")
    status: Optional["Status"] = Relationship(back_populates="task") # type: ignore

class TaskCreate(TaskBase):
    todolist_id: int = Field(description="Todo-List ID cant be empty")

class TaskRead(TaskBase):
    id: int