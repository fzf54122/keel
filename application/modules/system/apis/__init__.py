from fastapi import APIRouter

from .login import router as login_router
from .users import router as user_router

api_router = APIRouter()
api_router.include_router(login_router)
api_router.include_router(user_router)

__all__ = ["api_router"]
