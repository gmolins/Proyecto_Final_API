import os
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError
from auth.redis_client import redis_update_token
from log.logger import logger

ACCESS_SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 1

def _get_jti(sub: str, exp: datetime) -> str:
    """Generate a unique JWT ID using subject and expiration timestamp."""
    return f"{sub}_{int(exp.timestamp())}"

def create_access_token(data: dict, role: str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = _get_jti(data.get("sub", "unknown"), expire)
    to_encode.update({
        "exp": expire,
        "role": role,
        "jti": jti
    })
    ttl = int(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds())
    redis_update_token("access", jti, ttl, f"Validity: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    return jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = _get_jti(data.get("sub", "unknown"), expire)
    to_encode.update({
        "exp": expire,
        "jti": jti
    })
    ttl = int(timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS).total_seconds())
    redis_update_token("refresh", jti, ttl, f"Validity: {REFRESH_TOKEN_EXPIRE_DAYS} days")
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
def decode_access_token(token: str):
    try:
        return jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        logger.info(f"Attempted use of expired token: {token}")
        return None

def decode_refresh_token(token: str):
    try:
        return jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        logger.info(f"Attempted use of expired token: {token}")
        return None
    
def revoke_token(token: str, token_type: str):
    try:
        key = REFRESH_SECRET_KEY if token_type == "refresh" else ACCESS_SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = payload.get("exp") # Check if token is supposed to expire
        if jti and exp:
            redis_update_token(token_type, jti, 5, "Validity: Revoked")
    except ExpiredSignatureError:
        logger.info(f"Revoke attempt of already expired token: {token}")
