# -*- coding: utf-8 -*-
"""Keel pagination wrappers over fast_generic_api."""

from fast_generic_api.core.pagination import LimitOffsetPagination


class KeelPagination(LimitOffsetPagination):
    """脚手架默认分页。"""

    default_limit = 20
    max_limit = 20


class LimitOffsetFreePagination(LimitOffsetPagination):
    max_limit = 10_000


class LimitOffsetMax2000Pagination(LimitOffsetPagination):
    max_limit = 2000


class LimitOffsetMaxDefaultPagination(KeelPagination):
    """兼容旧名，业务可继续用这个。"""

    pass
