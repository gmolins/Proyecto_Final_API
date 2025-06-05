from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
import pandas as pd
from io import BytesIO
from jinja2 import Template
from sqlmodel import Session
from xhtml2pdf import pisa
from auth.dependencies import get_current_user
from db.database import get_session
from models.order import OrderCreate, OrderRead
from utils.api_client import fetch_product_data  # Importar la función desde el archivo auxiliar
from pathlib import Path

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
        sort_order: Optional[str] = Query("desc", description="(asc/desc)")
    ):
    try:
        product_data = await fetch_product_data()

        filtered = product_data.get("products")

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
"""
@router.post("/order", response_model=OrderRead)
async def add_product_by_id(order: OrderCreate, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    try:
        product_data = await fetch_product_data()

        filtered = product_data.get("products")

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

        return filtered
    except Exception as e:
        return {"error": str(e)}
"""