import copy
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session
import uvicorn
import pandas as pd
from io import BytesIO
from jinja2 import Template
from xhtml2pdf import pisa
from pathlib import Path

from auth.dependencies import get_current_user, require_ownership_or_admin
from crud.order import get_order_by_id
from crud.status import get_status_by_id
from db.database import get_session

router = APIRouter()

@router.get("/reporting/excel/{order_id}")
def get_order_excel(order_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

    require_ownership_or_admin(order.user_id, current_user)

    if not order.products:
        raise HTTPException(status_code=422, detail=f"Order with ID {order_id} has no products")

    buffer = BytesIO()
    df = pd.DataFrame(order.products)
    df["subtotal"] = df["price"] * df["quantity"]
    df = df[["id", "title", "price", "quantity", "subtotal"]]
    df.loc[len(df)] = ['', '', '', 'Total', df["subtotal"].sum()]

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=True, sheet_name="Order Data")
    buffer.seek(0)
    # Enviar el archivo Excel al cliente
    return Response(
        buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=order_data_{order_id}_{datetime.today().date()}.xlsx"}
    )

@router.get("/reporting/csv/{order_id}")
async def get_order_csv(order_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

    require_ownership_or_admin(order.user_id, current_user)

    if not order.products:
        raise HTTPException(status_code=422, detail=f"Order with ID {order_id} has no products")

    # Generar el archivo CSV en memoria
    buffer = BytesIO()
    df = pd.DataFrame(order.products)
    df["subtotal"] = df["price"] * df["quantity"]
    df = df[["id", "title", "price", "quantity", "subtotal"]]
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    # Enviar el archivo CSV al cliente
    return Response(
        buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=order_data_{order_id}_{datetime.today().date()}.csv"}
    )

@router.get("/reporting/pdf/{order_id}")
async def get_order_pdf(order_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    order = get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")
    
    require_ownership_or_admin(order.user_id, current_user)

    if not order.products:
        raise HTTPException(status_code=422, detail=f"Order with ID {order_id} has no products")
    
    # Cargar la plantilla HTML desde el archivo externo
    template_path = Path("templates/pdf_template.html")
    html_template = template_path.read_text(encoding="utf-8")
    template = Template(html_template)
        
    df = pd.DataFrame(order.products)
    df["subtotal"] = df["price"] * df["quantity"]
    df = df[["id", "title", "price", "quantity", "subtotal"]]
    order_rows = list(zip(
        df["id"].values,
        df["title"].values,
        df["price"].values,
        df["quantity"].values,
        df["subtotal"].values
    ))
    
    order_status = 'Unknown'
    if order.status_id:
        status = get_status_by_id(session, order.status_id)
        if status:
            order_status = status.name

    order_total = df["subtotal"].sum()
    rendered_html = template.render(rows=order_rows, id=order_id, status=order_status, total=order_total)
    
    # Convertir el HTML a PDF con xhtml2pdf
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_buffer)
    if pisa_status.err:
        return {"error": "Error al generar el PDF"}
    pdf_buffer.seek(0)
    
    # Enviar el archivo PDF al cliente
    return Response(
        pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=order_data_{order_id}.pdf"}
    )