# -*- coding: utf-8 -*-
"""HTTP middlewares."""

from __future__ import annotations

import json
import time
from collections.abc import AsyncGenerator
from typing import Any

from fastapi.responses import Response, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from common.core.task import KeelTask
from common.logger import LogContext, logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if request.url.path in {"/docs", "/redoc"}:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' data: https://cdn.jsdelivr.net https://unpkg.com; "
                "connect-src 'self'; "
                "worker-src 'self' blob:; "
                "child-src 'self' blob:"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            )
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = LogContext.set_request_id()
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms}ms)"
        )
        LogContext.clear()
        return response


class SimpleBaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):
        return self.app

    async def after_request(self, request: Request):
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    async def before_request(self, request):
        await KeelTask.init_bg_tasks_obj()

    async def after_request(self, request):
        await KeelTask.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    """Persist request audit logs when AuditLog model is available."""

    def __init__(self, app, methods: list[str], exclude_paths: list[str]):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths
        self.max_body_size = 1024 * 1024

    async def get_request_args(self, request: Request) -> dict:
        args: dict[str, Any] = dict(request.query_params)
        if request.method in {"POST", "PUT", "PATCH"}:
            content_type = request.headers.get("content-type", "")
            if "multipart/form-data" in content_type:
                return args
            try:
                body = await request.json()
                if isinstance(body, dict):
                    args.update(body)
            except Exception:
                pass
        return args

    def lenient_json(self, v: Any) -> Any:
        if isinstance(v, str | bytes):
            try:
                return json.loads(v)
            except (ValueError, TypeError):
                return v
        return v

    async def _async_iter(self, items: list[bytes]) -> AsyncGenerator[bytes, None]:
        for item in items:
            yield item

    async def get_response_body(self, response: Response) -> Any:
        if isinstance(response, StreamingResponse):
            return {"message": "[Streaming Response]"}
        try:
            if hasattr(response, "body"):
                body = response.body
            else:
                return {"message": "[No body]"}
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > self.max_body_size:
                return {"message": "Response too large to log"}
            return self.lenient_json(body)
        except Exception:
            return {"message": "[Unable to read response body]"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in self.methods:
            return await call_next(request)
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        started = time.perf_counter()
        request_args = await self.get_request_args(request)
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        try:
            from application.db.session import async_session_factory
            from application.modules.rbac.models.audit_log import AuditLogModel

            response_body = await self.get_response_body(response)
            async with async_session_factory() as session:
                log = AuditLogModel(
                    username=None,
                    module=request.url.path.split("/")[3] if len(request.url.path.split("/")) > 3 else "api",
                    summary=request.url.path,
                    method=request.method,
                    path=request.url.path,
                    host=request.client.host if request.client else None,
                    status=response.status_code,
                    response_time=elapsed_ms,
                    request_args=request_args,
                    response_body=response_body if isinstance(response_body, dict) else {"raw": str(response_body)},
                )
                session.add(log)
                await session.commit()
        except Exception as e:
            logger.debug(f"Audit log skipped: {e}")
        return response
