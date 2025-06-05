from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column
from sqlmodel import Relationship, SQLModel, Field
from typing import Any, Dict, Optional

class OrderBase(SQLModel):
    created_at: datetime
    product_data: Optional[Dict] = Field(default=None, sa_column=Column(JSONB))

class Order(OrderBase, table=True):
    id: int = Field(default=None, primary_key=True)
    status_id: Optional[int] = Field(default=None, foreign_key="status.id")
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="order") # type: ignore
    status: Optional["Status"] = Relationship(back_populates="order") # type: ignore

class OrderCreate(OrderBase):
    user_name: str = Field(..., min_length=3, max_length=100, description="User name cant be empty")

class OrderRead(OrderBase):
    id: int
    status_id: Optional[int] = Field(default=None, foreign_key="status.id")
    user_id: int = Field(foreign_key="user.id")
