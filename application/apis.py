# -*- coding: utf-8 -*-
from fastapi import APIRouter

from application.modules.demo.apis import api_router as demo_router
from application.modules.rbac.apis import api_router as rbac_router
from application.modules.system.apis import api_router as system_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(rbac_router)
api_router.include_router(demo_router)

__all__ = ["api_router"]
