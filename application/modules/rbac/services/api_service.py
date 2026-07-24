# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi.routing import APIRoute, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.db.backend import get_current_session
from application.modules.rbac.models import ApiModel, RoleModel
from common.core.service import KeelService
from common.logger import logger


def iter_api_routes(routes, prefix: str = ""):
    """递归展开 FastAPI 嵌套 include_router，带上完整 path 前缀。"""
    for route in routes:
        if isinstance(route, APIRoute):
            path = f"{prefix.rstrip('/')}/{route.path_format.lstrip('/')}" if prefix else route.path_format
            if not path.startswith("/"):
                path = "/" + path
            yield route, path
            continue

        if hasattr(route, "original_router") and isinstance(route.original_router, APIRouter):
            ctx = getattr(route, "include_context", None)
            child_prefix = prefix
            if ctx is not None and getattr(ctx, "prefix", None):
                child_prefix = f"{prefix.rstrip('/')}/{ctx.prefix.lstrip('/')}".rstrip("/")
                if not child_prefix.startswith("/"):
                    child_prefix = "/" + child_prefix if child_prefix else ""
            yield from iter_api_routes(route.original_router.routes, child_prefix)
            continue

        if hasattr(route, "routes"):
            yield from iter_api_routes(route.routes, prefix)


class ApiService(KeelService[ApiModel]):
    def __init__(self):
        super().__init__(model=ApiModel)

    async def refresh_api(self, app) -> int:
        session = get_current_session()
        exclude_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health",
        }

        current_routes: list[tuple[str, str, str, str]] = []
        for route, path in iter_api_routes(app.routes):
            if path in exclude_paths:
                continue
            methods = sorted(m for m in (route.methods or set()) if m not in {"HEAD", "OPTIONS"})
            if not methods:
                continue
            method = methods[0]
            summary = route.summary or "无描述"
            tags = list(route.tags)[0] if route.tags else "未分类"
            current_routes.append((method, path, summary, tags))

        route_keys = {(m, p) for m, p, _, _ in current_routes}
        result = await session.execute(select(ApiModel))
        existing = list(result.scalars().all())

        for api in existing:
            if (api.method, api.path) not in route_keys:
                logger.debug(f"API Deleted {api.method} {api.path}")
                await session.delete(api)

        existing_map = {(a.method, a.path): a for a in existing if (a.method, a.path) in route_keys}
        for method, path, summary, tags in current_routes:
            api_obj = existing_map.get((method, path))
            if api_obj:
                api_obj.summary = summary
                api_obj.tags = tags
            else:
                logger.debug(f"API Created {method} {path}")
                session.add(ApiModel(method=method, path=path, summary=summary, tags=tags))
        await session.flush()
        return len(current_routes)

    async def grant_all_apis_to_admin(self) -> None:
        """把当前全部 API 赋给「管理员」角色（幂等）。"""
        session = get_current_session()
        result = await session.execute(
            select(RoleModel)
            .options(selectinload(RoleModel.apis))
            .where(RoleModel.name == "管理员")
        )
        admin_role = result.scalar_one_or_none()
        if not admin_role:
            return
        apis = list((await session.execute(select(ApiModel))).scalars().all())
        admin_role.apis = apis
        await session.flush()
        logger.info(f"Admin role granted {len(apis)} APIs")
