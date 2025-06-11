from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlmodel import Session
from auth.jwt import create_access_token, create_refresh_token, decode_refresh_token, revoke_token, decode_access_token
from auth.hashing import hash_password, verify_password
from db.database import get_session
from auth.dependencies import get_current_user, oauth2_scheme, require_ownership_or_admin
from models.user import User, UserCreate, UserRead
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, session: Session = Depends(get_session)):
    query = select(User).where(User.username == user.username) # type: ignore
    existing_user = session.scalars(query).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role="user",
        created_at=datetime.now()
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    query = select(User).where(User.username == form_data.username) # type: ignore
    user = session.scalars(query).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "id": user.id}, role=user.role)
    refresh_token = create_refresh_token({"sub": user.username})
    user.refresh_token = refresh_token
    session.add(user)
    session.commit()
    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(refresh_token: str, session: Session = Depends(get_session)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    query = select(User).where(User.refresh_token == refresh_token) # type: ignore
    user = session.scalars(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_access_token = create_access_token({"sub": user.username}, role=user.role)

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user), token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    query = select(User).where(User.username == current_user["sub"])
    user = session.scalars(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    revoke_token(token, "access")
    
    if user.refresh_token:
        revoke_token(user.refresh_token, "refresh")
        user.refresh_token = None
        session.add(user)
        session.commit()

    return {"message": "Successfully logged out"}

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_view(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
def forgot_password(email: str = Form(...), session: Session = Depends(get_session)):
    query = select(User).where(User.email == email) # type: ignore
    user = session.scalars(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    # Generar token de recuperación
    token = create_access_token({"sub": user.email}, role="reset")
    
    # Devolver el token directamente
    return {"message": "Use this token to reset your password", "token": token}

@router.post("/reset-password")
def reset_password(token: str = Form(...), new_password: str = Form(...), session: Session = Depends(get_session)):
    payload = decode_access_token(token)
    if not payload or payload.get("role") != "reset":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    query = select(User).where(User.email == payload["sub"])
    user = session.scalars(query).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Revocar token de reset
    revoke_token(token, "access")

    # Actualizar contraseña
    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.commit()

    return RedirectResponse(url="/", status_code=303)
