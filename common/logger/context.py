# -*- coding: utf-8 -*-
"""Request-scoped logging context."""

from __future__ import annotations

import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
user_id_var: ContextVar[str] = ContextVar("user_id", default="-")


class LogContext:
    @staticmethod
    def generate_request_id() -> str:
        return str(uuid.uuid4())[:8]

    @staticmethod
    def set_request_id(request_id: str | None = None) -> str:
        if not request_id:
            request_id = LogContext.generate_request_id()
        request_id_var.set(request_id)
        return request_id

    @staticmethod
    def set_user_id(user_id: str | None) -> None:
        user_id_var.set(str(user_id) if user_id else "-")

    @staticmethod
    def get_request_id() -> str:
        return request_id_var.get()

    @staticmethod
    def get_user_id() -> str:
        return user_id_var.get()

    @staticmethod
    def get_logger():
        from common.logger.log import logger

        return logger.bind(
            request_id=LogContext.get_request_id(),
            user_id=LogContext.get_user_id(),
        )

    @staticmethod
    def clear() -> None:
        request_id_var.set("-")
        user_id_var.set("-")


class RequestLogContext:
    def __init__(self, request_id: str | None = None, user_id: str | None = None):
        self.request_id = request_id
        self.user_id = user_id
        self.old_request_id = None
        self.old_user_id = None

    def __enter__(self):
        self.old_request_id = LogContext.get_request_id()
        self.old_user_id = LogContext.get_user_id()
        LogContext.set_request_id(self.request_id)
        LogContext.set_user_id(self.user_id)
        return LogContext.get_logger()

    def __exit__(self, exc_type, exc_val, exc_tb):
        request_id_var.set(self.old_request_id or "-")
        user_id_var.set(self.old_user_id or "-")


def get_context_logger():
    return LogContext.get_logger()


def with_request_context(request_id: str | None = None, user_id: str | None = None):
    return RequestLogContext(request_id, user_id)
