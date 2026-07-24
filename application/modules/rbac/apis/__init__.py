from fastapi import APIRouter

from .apis import router as apis_router
from .audit_logs import router as audit_router
from .depts import router as depts_router
from .menus import router as menus_router
from .roles import router as roles_router

api_router = APIRouter()
api_router.include_router(roles_router)
api_router.include_router(menus_router)
api_router.include_router(apis_router)
api_router.include_router(depts_router)
api_router.include_router(audit_router)

__all__ = ["api_router"]
