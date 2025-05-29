import time
from fastapi import Request
from .logger import logger

async def log_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = round((time.time() - start_time) * 1000, 2)
    log_data = {
        "method": request.method,
        "url": request.url.path,
        "status_code": response.status_code,
        "duration_ms": process_time
    }

    logger.info(f"{log_data['method']} {log_data['url']} - {log_data['status_code']} - {log_data['duration_ms']}ms")
    return response
