import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from auth.redis_client import revoke_token as redis_revoke_token, is_token_revoked

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def _get_jti(sub: str, exp: datetime) -> str:
    """Generate a unique JWT ID using subject and expiration timestamp."""
    return f"{sub}_{int(exp.timestamp())}"

def create_access_token(data: dict, role: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    jti = _get_jti(data.get("sub", "unknown"), expire)
    to_encode.update({
        "exp": expire,
        "role": role,
        "jti": jti
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = _get_jti(data.get("sub", "unknown"), expire)
    to_encode.update({
        "exp": expire,
        "jti": jti
    })
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            raise JWTError("Token has been revoked")
        return payload
    except JWTError:
        return None

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti and is_token_revoked(jti):
            raise JWTError("Refresh token has been revoked")
        return payload
    except JWTError:
        return None

def revoke_token(token: str, refresh: bool = False):
    """Revoke a token and store its jti in Redis until it expires."""
    try:
        key = REFRESH_SECRET_KEY if refresh else SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            ttl = int(exp - datetime.now(timezone.utc).timestamp())
            redis_revoke_token(jti, ttl)
    except JWTError:
        pass
