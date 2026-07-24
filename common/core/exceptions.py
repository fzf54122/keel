# -*- coding: utf-8 -*-
"""Global exception handlers."""

from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from fast_generic_api.core.exceptions import FastAutoException
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette.responses import Response

from conf import settings


class SettingNotFound(Exception):
    pass


class KeelException(FastAutoException):
    """脚手架业务异常基类。"""

    status_code = 400
    code = 40000
    detail = "业务错误"


class ObjectExistException(KeelException):
    code = 20010
    detail = "对象已存在"


class ObjectNotFoundException(KeelException):
    code = 20020
    detail = "没有找到对应对象"


async def NotFoundHandle(req: Request, exc: NoResultFound) -> JSONResponse:
    msg = f"Object not found: {exc}" if settings.DEBUG else "资源不存在"
    return JSONResponse(content={"code": 404, "status": "error", "msg": msg, "data": None}, status_code=404)


async def HttpExcHandle(request: Request, exc: HTTPException):
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        return Response(status_code=exc.status_code, headers=exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "status": "error", "msg": exc.detail, "data": None},
    )


async def IntegrityHandle(request: Request, exc: IntegrityError):
    msg = f"IntegrityError: {exc}" if settings.DEBUG else "数据完整性错误"
    return JSONResponse(
        content={"code": 500, "status": "error", "msg": msg, "data": None},
        status_code=500,
    )


async def RequestValidationHandle(_: Request, exc: RequestValidationError) -> JSONResponse:
    msg = f"RequestValidationError: {exc}" if settings.DEBUG else "请求参数验证失败"
    return JSONResponse(
        content={"code": 422, "status": "error", "msg": msg, "data": None},
        status_code=422,
    )


async def ResponseValidationHandle(_: Request, exc: ResponseValidationError) -> JSONResponse:
    msg = f"ResponseValidationError: {exc}" if settings.DEBUG else "服务器响应格式错误"
    return JSONResponse(
        content={"code": 500, "status": "error", "msg": msg, "data": None},
        status_code=500,
    )


async def GlobalExceptionHandle(request: Request, exc: Exception):
    if isinstance(exc, FastAutoException):
        return JSONResponse(
            status_code=getattr(exc, "status_code", 400) or 400,
            content={
                "code": getattr(exc, "code", 40000),
                "status": "error",
                "msg": getattr(exc, "detail", str(exc)),
                "data": None,
                "path": request.url.path if settings.DEBUG else None,
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "status": "error",
            "msg": "Internal Server Error",
            "data": None,
            "detail": str(exc) if settings.DEBUG else None,
            "path": request.url.path,
        },
    )
