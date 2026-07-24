# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi.routing import APIRoute
from sqlalchemy import select

from application.modules.rbac.models import ApiModel
from application.db.backend import get_current_session
from common.core.service import KeelService
from common.logger import logger


class ApiService(KeelService[ApiModel]):
    def __init__(self):
        super().__init__(model=ApiModel)

    async def refresh_api(self, app) -> None:
        session = get_current_session()
        exclude_paths = {"/docs", "/redoc", "/openapi.json", "/favicon.ico"}

        current_routes: list[tuple[str, str, str, str]] = []
        for route in app.routes:
            if isinstance(route, APIRoute) and route.path not in exclude_paths:
                method = list(route.methods)[0]
                path = route.path_format
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

        existing_map = {(a.method, a.path): a for a in existing}
        for method, path, summary, tags in current_routes:
            api_obj = existing_map.get((method, path))
            if api_obj:
                api_obj.summary = summary
                api_obj.tags = tags
            else:
                logger.debug(f"API Created {method} {path}")
                session.add(
                    ApiModel(method=method, path=path, summary=summary, tags=tags)
                )
        await session.flush()
