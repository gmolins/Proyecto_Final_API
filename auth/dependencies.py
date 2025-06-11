from typing import Any
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from auth.jwt import decode_access_token
from db.database import get_session
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

def require_role(required_role: str):
    def role_dependency(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_dependency

def require_ownership_or_admin(resource_identifier: str | int, current_user: dict):
    is_admin = current_user["role"] == "admin"
    is_owner = (resource_identifier == current_user["sub"] or resource_identifier == current_user["id"]) 

    if not (is_admin or is_owner):
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    return None