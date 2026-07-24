# -*- coding: utf-8 -*-
"""Keel ViewSet 基类 — 业务只声明差异字段。

公共默认：
- uuid 查找
- SQLAlchemy backend
- 默认分页
- DISABLE_AUTH 时跳过鉴权
- 软删过滤（模型含 is_deleted 时）
- get_queryset 扩展钩子 filter_queryset_for_user

业务示例::

    class ItemViewSet(KeelViewSet):
        router = router
        prefix = "/items"
        queryset = ItemModel
        filter_class = ItemFilter
        serializer_class = ItemSerializers
"""

from __future__ import annotations

from typing import Any

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

    # 是否自动过滤 is_deleted=False（模型无该字段则忽略）
    soft_delete_filter: bool = True

    def filter_queryset_for_user(self, queryset: Any) -> Any:
        """租户/数据权限扩展点。默认原样返回。

        业务可覆盖::

            def filter_queryset_for_user(self, queryset):
                user = self.context.get("user")
                if user and not user.is_superuser:
                    return self.backend.filter(queryset, owner_id=user.id)
                return queryset
        """
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.soft_delete_filter:
            model = self.backend.resolve_model(queryset)
            meta = self.backend.get_model_meta(model)
            fields = getattr(meta, "fields_map", {}) if meta is not None else {}
            # super() 通常已处理 is_deleted；这里保证自定义 queryset 也覆盖
            if "is_deleted" in fields:
                queryset = self.backend.filter(queryset, is_deleted=False)
        return self.filter_queryset_for_user(queryset)
