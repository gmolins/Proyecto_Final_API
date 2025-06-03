import redis

# Conexión simple, ajusta según configuración real
r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

def redis_update_token(token_type: str, jti: str, ttl: int, status: str):
    """Store token in Redis until expiration (TTL)"""
    try:
        r.setex(f"{token_type}:{jti}", ttl, f"{status}")
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")