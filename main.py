from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from auth.dependencies import get_current_user
from dotenv import load_dotenv
from log.logger import logger
from log.middleware import log_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from routes import auth, task, todo, user, status

import uvicorn

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add our logging middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=log_middleware)

logger.info('Starting API...')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Configuración de Jinja2
templates = Jinja2Templates(directory="templates")

# Definir las rutas de la APIs
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(task.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(todo.router, prefix="/api/todos", tags=["Todo-Lists"])
app.include_router(user.router, prefix="/api/users", tags=["Users"])
app.include_router(status.router, prefix="/api/status", tags=["Status"])

@app.get("/", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# Protect existing routes
@app.get("/protected-route")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}

# Manejo de excepciones globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "error": str(exc)},
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
