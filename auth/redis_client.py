import redis

# Conexión simple, ajusta según configuración real
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

def revoke_token(jti: str, exp: int):
    """Guarda el token revocado en Redis hasta su expiración."""
    r.setex(f"revoked:{jti}", exp, "revoked")

def is_token_revoked(jti: str) -> bool:
    """Verifica si el token fue revocado."""
    try:
        return r.exists(f"revoked:{jti}") == 1
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        # Optional: treat Redis as unavailable = allow access or deny by default
        return False  # or True if you prefer fail-closed
