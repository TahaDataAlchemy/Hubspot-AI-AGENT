from fastapi import APIRouter
from modules.auth.routes import router as auth_router

API_ROUTER = APIRouter(tags=["Auth"])
API_ROUTER.include_router(auth_router)
