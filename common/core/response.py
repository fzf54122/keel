# -*- coding: utf-8 -*-
"""脚手架统一响应规范。

业务层只允许使用 ``KeelResponse``，禁止直接依赖 fast_generic_api 的 Response。

用法:
    return KeelResponse(data=user)
    return KeelResponse(data=JWTOut(...), msg="登录成功")
    return KeelResponse(msg="退出登录成功")
    return KeelResponse(data=None, code=400, status="error", msg="密码错误")
    return KeelResponse(data={"total": 10, "results": items})
"""

from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class KeelResponse(JSONResponse):
    """统一响应信封: ``{code, status, data, msg}``

    字段与 fast_generic_api 对齐；入口与扩展由脚手架定义。
    """

    def __init__(
        self,
        data: Any = None,
        *,
        code: int = 200,
        status: str = "success",
        msg: str = "OK",
        status_code: int | None = None,
        **extra: Any,
    ):
        if isinstance(data, BaseModel):
            data = data.model_dump()

        content: dict[str, Any] = {
            "code": code,
            "status": status,
            "data": jsonable_encoder(data),
            "msg": msg,
        }
        if extra:
            content.update(jsonable_encoder(extra))

        # 业务码在 body.code；HTTP 状态默认 200，需要 201/401 时显式传 status_code
        super().__init__(content=content, status_code=status_code or 200)
