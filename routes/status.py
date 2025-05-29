from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session

from db.database import get_session
from models.status import Status, StatusCreate, StatusRead
from crud.status import (
    create_status,
    delete_status_by_id,
    get_status_by_id,
    get_status_by_name,
    get_status,
    update_status_by_id
)
from auth.dependencies import get_current_user, require_role  # Import role-based dependency

router = APIRouter()

@router.post("/", response_model=StatusRead)
def create(status: StatusCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        status_data = Status(**status.model_dump())
        created_status = create_status(session, status_data)
        session.refresh(created_status)  # Refresh to load relationships
        return created_status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=list[StatusRead])
def read_all(session: Session = Depends(get_session)):
    try:
        return get_status(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{status_id}", response_model=StatusRead)
def read(status_id: int, session: Session = Depends(get_session)):
    try:
        status = get_status_by_id(session, status_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Task with ID {status_id} not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/name/{name}", response_model=StatusRead)
def read_by_title(name: str, session: Session = Depends(get_session)):
    try:
        status = get_status_by_name(session, name)
        if not status:
            raise HTTPException(status_code=404, detail=f"Statys with name '{name}' not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/{status_id}", response_model=Status)
def update(
    status_id: int,
    status_data: dict = Body(
        ...,
        examples=[
            {
                "title": "Updated Status Name",
                "content": "Updated content for the Status"
            }
        ]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin"))
):
    try:
        updated_status = update_status_by_id(session, status_id, status_data)
        if not updated_status:
            raise HTTPException(status_code=404, detail=f"Task with ID {status_id} not found")
        return updated_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/{status_id}", response_model=Status)
def delete(status_id: int, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    try:
        deleted_status = delete_status_by_id(session, status_id)
        if not deleted_status:
            raise HTTPException(status_code=404, detail=f"Status with ID {status_id} not found")
        return deleted_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")