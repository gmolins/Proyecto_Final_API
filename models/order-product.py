from datetime import datetime
from sqlmodel import Relationship, SQLModel, Field
from typing import Optional

class OrderProduct(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int
