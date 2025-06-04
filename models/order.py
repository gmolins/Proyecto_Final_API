from datetime import datetime
from sqlalchemy import Column, JSON, ARRAY, Integer
from sqlmodel import Relationship, SQLModel, Field
from typing import Any, Dict, Optional

class OrderBase(SQLModel):
    created_at: datetime
    pass

class Order(OrderBase, table=True):
    id: int = Field(default=None, primary_key=True)
    status_id: Optional[int] = Field(default=None, foreign_key="status.id")
    product_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    user_id: int = Field(foreign_key="user.id")

    user: "User" = Relationship(back_populates="order") # type: ignore
    status: Optional["Status"] = Relationship(back_populates="order") # type: ignore

class OrderCreate(OrderBase):
    user_name: str = Field(..., min_length=3, max_length=100, description="User name cant be empty")

class OrderRead(OrderBase):
    id: int
    product_ids: list[int] | None
    status_id: int
