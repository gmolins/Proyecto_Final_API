from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from db.database import get_session
from models.order import Order, OrderCreate, OrderRead
from crud.user import get_user_by_name
from crud.order import (
    create_order,
    get_orders,
    get_order_by_id,
    get_orders_by_user_name,
    update_order,
    delete_order
)
from auth.dependencies import get_current_user, require_role  # Import role-based dependency

router = APIRouter()

@router.post("/", response_model=OrderRead)
def create(order: OrderCreate, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    user = get_user_by_name(session, order.user_name)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with name '{order.user_name}' not found")
    
    order_data = Order(**order.model_dump(exclude={"user_name"}), user_id=user.id, status_id=1)
    created_order = create_order(session, order_data)
    session.refresh(created_order)  # Refresh to load relationships
    return created_order

@router.get("/", response_model=list[OrderRead])
def read_all(session: Session = Depends(get_session)):
    return get_orders(session)

@router.get("/{order_id}", response_model=OrderRead)
def read(order_id: int, session: Session = Depends(get_session)):
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"No orders found for {order_id}")
    return order

@router.get("/user/{user_name}", response_model=list[OrderRead])
def read_by_user_name(user_name: str, session: Session = Depends(get_session)):
    orders = get_orders_by_user_name(session, user_name)
    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for user '{user_name}'")
    return orders

@router.put("/{order_id}", response_model=Order)
def update(
    order_id: int,
    order_data: dict = Body(examples=[
        {
            "created_at": "2025-06-05T13:30:05.717Z",
            "status_id": 0,
            "product_data": {
                "additionalProp1": {}
            }
        }
    ]),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    updated_order = update_order(session, order_id, order_data)
    if not updated_order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    return updated_order

@router.delete("/{order_id}", response_model=Order)
def delete(order_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    deleted_order = delete_order(session, order_id)
    if not deleted_order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    return deleted_order
