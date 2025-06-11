from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from auth.dependencies import get_current_user, require_ownership_or_admin
from crud.order import get_order_by_id, update_order_by_id
from db.database import get_session
from models.order import OrderRead
from utils.api_client import fetch_product_data  # Importar la función desde el archivo auxiliar
import copy

router = APIRouter()

@router.get("/", response_model=list[dict])
async def get_all_products(
        id: Optional[int] = Query(None),
        title: Optional[str] = Query(None, description="Filter by product title"),
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        category: Optional[str] = Query(None),
        tag: Optional[str] = Query(None),
        brand: Optional[str] = Query(None),
        sort_by: Optional[str] = Query(None, description="e.g. price, rating"),
        sort_order: Optional[str] = Query(None, description="(asc/desc)"),
        skip: Optional[int] = Query(None),
        limit: Optional[int] = Query(None)
    ):
    try:
        product_data = await fetch_product_data()

        filtered = product_data.get("products")

        if skip is not None and limit is not None:
            filtered = filtered[skip:skip+limit]
        if title:
            filtered = [p for p in filtered if title.lower() in p.get("title", "").lower()]
        if category:
            filtered = [p for p in filtered if p.get("category", "").lower() == category.lower()]
        if tag:
            filtered = [p for p in filtered if tag.lower() in [t.lower() for t in p.get("tags", [])]]
        if brand:
            filtered = [p for p in filtered if p.get("brand", "").lower() == brand.lower()]
        if min_price is not None:
            filtered = [p for p in filtered if isinstance(p.get("price"), (int, float)) and p["price"] >= min_price]
        if max_price is not None:
            filtered = [p for p in filtered if isinstance(p.get("price"), (int, float)) and p["price"] <= max_price]

        if sort_by:
            reverse = sort_order == "desc"
            try:
                filtered.sort(key=lambda p: p.get(sort_by, 0), reverse=reverse)
            except TypeError:
                raise HTTPException(status_code=400, detail=f"Cannot sort by field: {sort_by}")
            
        if id:
            for p in filtered:
                if p.get("id", "") == id:
                    return [p]
            raise HTTPException(status_code=404, detail=f"Product with ID {id} not found")

        return filtered
    except Exception as e:
        return {"error": str(e)}

@router.post("/order", response_model=OrderRead)
async def add_product_by_id(order_id:int, product_id: int, product_quantity:int = Query(gt=0), session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    product_data = await fetch_product_data()
    filtered = product_data.get("products")
    for p in filtered:
        if p.get("id", "") == product_id:
            order = get_order_by_id(session, order_id)
            if not order:
                raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
            
            require_ownership_or_admin(order.user_id, current_user)

            if order.status_id != 1: # Check if order is already placed
                raise HTTPException(status_code=403, detail=f"Order with ID {order_id} is already placed!")

            updated_products = copy.deepcopy(order.products) if order.products else []

            # Flag to track if product exists
            product_found = False

            for i, product in enumerate(updated_products):
                if p.get("id", "") == product.get("id", ""):
                    updated_products[i]["title"] = p.get("title")
                    updated_products[i]["quantity"] += product_quantity
                    updated_products[i]["price"] = p.get("price")
                    product_found = True
                    break

            # If product is not already in the list, append it
            if not product_found:
                updated_products.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "quantity": product_quantity,
                    "price": p.get("price")
                })

            updated_order = update_order_by_id(session, order_id, {"products": updated_products})
            return updated_order
    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")