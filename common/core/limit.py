# -*- coding: utf-8 -*-
"""Rate limiting helpers."""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from conf import settings

limiter = Limiter(key_func=get_remote_address)


def apply_rate_limit(rate: str = "5/minute"):
    def decorator(func):
        if settings.DEBUG:
            return func
        return limiter.limit(rate)(func)

    return decorator
