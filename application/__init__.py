# -*- coding: utf-8 -*-
"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from common.core.app import make_middlewares, register_exceptions, register_routers
from common.core.bootstrap import init_data, shutdown_data
from common.core.exceptions import SettingNotFound

try:
    from conf import settings
except ImportError as e:
    raise SettingNotFound("Can not import settings") from e


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_data(app)
    yield
    await shutdown_data()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=app.title + " - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=app.title + " - ReDoc",
        )

    @app.get("/openapi.json", include_in_schema=False)
    async def get_open_api_endpoint():
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

    @app.get("/health", tags=["health"])
    async def health():
        from sqlalchemy import text

        from application.db.session import async_session_factory
        from common.core.cache import cache_manager

        db_ok = False
        redis_ok = False
        try:
            async with async_session_factory() as session:
                await session.execute(text("SELECT 1"))
                db_ok = True
        except Exception:
            db_ok = False
        try:
            redis_ok = bool(cache_manager.redis and await cache_manager.redis.ping())
        except Exception:
            redis_ok = False

        status = "ok" if db_ok else "degraded"
        return {
            "status": status,
            "app": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "checks": {"database": db_ok, "redis": redis_ok},
        }

    register_exceptions(app)
    register_routers(app, prefix="/api")
    return app


app = create_app()
