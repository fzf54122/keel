# -*- coding: utf-8 -*-
"""App wiring helpers: middleware, exceptions, routers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from application.apis import api_router
from application.db.session import async_session_factory
from common.core.exceptions import (
    GlobalExceptionHandle,
    HttpExcHandle,
    IntegrityHandle,
    NotFoundHandle,
    RequestValidationHandle,
    ResponseValidationHandle,
)
from common.core.limit import limiter
from common.core.middlewares import (
    BackGroundTaskMiddleware,
    HttpAuditLogMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from conf import settings
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError


class SQLAlchemySessionMiddleware(BaseHTTPMiddleware):
    """Bind AsyncSession to context for the whole request."""

    async def dispatch(self, request: Request, call_next):
        from application.db.backend import _session_ctx

        session = async_session_factory()
        token = _session_ctx.set(session)
        request.state.db = session
        try:
            response = await call_next(request)
            # 读请求不强制提交；写请求统一提交，避免空事务噪音
            if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
                await session.commit()
            return response
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            _session_ctx.reset(token)


def make_middlewares():
    return [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS_LIST,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(SQLAlchemySessionMiddleware),
        Middleware(SecurityHeadersMiddleware),
        Middleware(RequestLoggingMiddleware),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            exclude_paths=[
                "/api/auth/login/",
                "/api/auth/refresh/",
                "/docs",
                "/redoc",
                "/openapi.json",
            ],
        ),
    ]


def register_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(NoResultFound, NotFoundHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_exception_handler(Exception, GlobalExceptionHandle)


def register_routers(app: FastAPI, prefix: str = "/api") -> None:
    app.include_router(api_router, prefix=prefix)
