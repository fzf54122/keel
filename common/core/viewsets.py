# -*- coding: utf-8 -*-
"""Keel ViewSet 基类 — 业务只声明差异字段。"""

from __future__ import annotations

from typing import Any

from fast_generic_api.generics import CustomViewSet, GenericAPIView

from application.db.backend import backend_provider
from application.pagination import KeelPagination
from common.core.permission import DependPermisson


class KeelViewSet(CustomViewSet, GenericAPIView):
    """脚手架默认 ViewSet。

    permissions 始终挂 DependPermisson；是否跳过鉴权由 settings.DISABLE_AUTH
    在依赖内部运行时决定，避免 import 时固化空列表。
    """

    lookup_field = "uuid"
    loop_uuid_field = "uuid"
    ordering = ["-created_at"]
    pagination_class = KeelPagination
    backend_provider = staticmethod(backend_provider)
    permissions = [DependPermisson]

    soft_delete_filter: bool = True

    def filter_queryset_for_user(self, queryset: Any) -> Any:
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.soft_delete_filter:
            model = self.backend.resolve_model(queryset)
            meta = self.backend.get_model_meta(model)
            fields = getattr(meta, "fields_map", {}) if meta is not None else {}
            if "is_deleted" in fields:
                queryset = self.backend.filter(queryset, is_deleted=False)
        return self.filter_queryset_for_user(queryset)
