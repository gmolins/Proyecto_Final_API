from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session
from auth.dependencies import get_current_user, require_role
from db.database import get_session
from models.user import User, UserCreate
from auth.hashing import hash_password
from crud.user import (
    create_user,
    get_all_users_wp,
    get_user_by_mail,
    get_all_users,
    get_user_by_id,
    get_user_by_name,
    update_user_by_id,
    delete_user_by_id,
    update_user_by_name,
    delete_user_by_name,
)

router = APIRouter()

@router.post("/", response_model=User)
def create(user: UserCreate, session: Session = Depends(get_session), current_user: dict = Depends(require_role("admin"))):
    user_data = User(**user.model_dump(exclude={"password"}), 
                        hashed_password=hash_password(user.password), 
                        created_at=datetime.now(), 
                        role=user.role)
    return create_user(session, user_data)

@router.get("/", response_model=list[User])
def read_all(session: Session = Depends(get_session)):
    return get_all_users(session)
    
@router.get("/wp", response_model=list[User])
def read_all_wp(skip: int, limit: int, session: Session = Depends(get_session)):
    return get_all_users_wp(session, skip, limit)

@router.get("/{user_id}", response_model=User)
def read(user_id: int, session: Session = Depends(get_session)):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return user

@router.get("/name/{name}", response_model=User)
def read_by_name(name: str, session: Session = Depends(get_session)):
    user = get_user_by_name(session, name)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with name '{name}' not found")
    return user
    
@router.get("/email/{email}", response_model=User)
def read_by_email(email: str, session: Session = Depends(get_session)):
    user = get_user_by_mail(session, email)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email '{email}' not found")
    return user

@router.put("/{user_id}", response_model=User)
def update(
    user_id: int,
    user_data: dict = Body(
        ...,
        examples=[{
            "name": "Updated User Name",
            "email": "updated_email@example.com"
        }]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(require_role("admin"))
):
    updated_user = update_user_by_id(session, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return updated_user

@router.put("/name/{name}", response_model=User)
def update_by_name(
    name: str,
    user_data: dict = Body(
        ...,
        examples=[{
            "name": "Updated User Name",
            "email": "updated_email@example.com"
        }]
    ),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    updated_user = update_user_by_name(session, name, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"User with name '{name}' not found")
    return updated_user

@router.delete("/{user_id}", response_model=User)
def delete(user_id: int, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    deleted_user = delete_user_by_id(session, user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    return deleted_user

@router.delete("/name/{name}", response_model=User)
def delete_by_name(name: str, session: Session = Depends(get_session), current_user: dict = Depends(get_current_user)):
    deleted_user = delete_user_by_name(session, name)
    if not deleted_user:
        raise HTTPException(status_code=404, detail=f"User with name '{name}' not found")
    return deleted_user