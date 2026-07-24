# -*- coding: utf-8 -*-
"""Keel ViewSet 基类 — 业务只声明差异字段。

公共默认：
- uuid 查找
- SQLAlchemy backend
- 默认分页
- DISABLE_AUTH 时跳过鉴权

业务示例::

    class ItemViewSet(KeelViewSet):
        router = router
        prefix = "/items"
        queryset = ItemModel
        serializer_class = ItemSerializers
        serializer_create_class = ItemCreateSerializers
        serializer_update_class = ItemUpdateSerializers
"""

from __future__ import annotations

from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.db.backend import backend_provider
from application.pagination import KeelPagination
from common.core.permission import DependPermisson
from conf import settings


class KeelViewSet(CustomViewSet, GenericAPIView):
    """脚手架默认 ViewSet。"""

    lookup_field = "uuid"
    loop_uuid_field = "uuid"
    ordering = ["-created_at"]
    pagination_class = KeelPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [] if settings.DISABLE_AUTH else [DependPermisson]
