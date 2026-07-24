#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate a business module skeleton.

Usage:
    python scripts/new_module.py order
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "application" / "modules"


def main(name: str) -> None:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
        raise SystemExit("module name must be snake_case, e.g. order / payment_receipt")

    base = MODULES / name
    if base.exists():
        raise SystemExit(f"module already exists: {base}")

    for sub in ("apis", "models", "serializers", "services"):
        (base / sub).mkdir(parents=True)

    class_prefix = "".join(part.capitalize() for part in name.split("_"))
    route = name.replace("_", "-")

    (base / "__init__.py").write_text(f'"""Business module: {name}."""\n')
    (base / "apis" / "__init__.py").write_text(
        f'''from fastapi import APIRouter

from .{name} import router as {name}_router

api_router = APIRouter()
api_router.include_router({name}_router)

__all__ = ["api_router"]
'''
    )
    (base / "apis" / f"{name}.py").write_text(
        f'''# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

from application.modules.{name}.models import {class_prefix}Model
from application.modules.{name}.serializers import (
    {class_prefix}CreateSerializers,
    {class_prefix}Serializers,
    {class_prefix}UpdateSerializers,
)
from common.core.viewsets import KeelViewSet

router = APIRouter(tags=["{class_prefix}"])


class {class_prefix}ViewSet(KeelViewSet):
    router = router
    prefix = "/{route}"
    queryset = {class_prefix}Model
    serializer_class = {class_prefix}Serializers
    serializer_create_class = {class_prefix}CreateSerializers
    serializer_update_class = {class_prefix}UpdateSerializers
'''
    )
    (base / "models" / "__init__.py").write_text(
        f'from .{name} import {class_prefix}Model\n\n__all__ = ["{class_prefix}Model"]\n'
    )
    (base / "models" / f"{name}.py").write_text(
        f'''# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class {class_prefix}Model(KeelModel):
    __tablename__ = f"{{settings.TABLE_PREFIX}}{name}"

    name: Mapped[str] = mapped_column(String(100), index=True, default="")
'''
    )
    (base / "serializers" / "__init__.py").write_text(
        f'''from .{name} import (
    {class_prefix}CreateSerializers,
    {class_prefix}Serializers,
    {class_prefix}UpdateSerializers,
)

__all__ = [
    "{class_prefix}Serializers",
    "{class_prefix}CreateSerializers",
    "{class_prefix}UpdateSerializers",
]
'''
    )
    (base / "serializers" / f"{name}.py").write_text(
        f'''# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from common.core.schemas import KeelSchemas


class {class_prefix}Serializers(KeelSchemas):
    id: int | None = None
    uuid: UUID | str | None = None
    name: str | None = None
    description: str | None = None
    is_active: bool | None = True
    created_at: datetime | None = None
    updated_at: datetime | None = None


class {class_prefix}CreateSerializers(KeelSchemas):
    name: str
    description: str | None = ""
    is_active: bool = True


class {class_prefix}UpdateSerializers(KeelSchemas):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
'''
    )
    (base / "services" / "__init__.py").write_text(
        f'from .{name}_service import {class_prefix}Service\n\n__all__ = ["{class_prefix}Service"]\n'
    )
    (base / "services" / f"{name}_service.py").write_text(
        f'''# -*- coding: utf-8 -*-
from application.modules.{name}.models import {class_prefix}Model
from common.core.service import KeelService


class {class_prefix}Service(KeelService[{class_prefix}Model]):
    def __init__(self):
        super().__init__(model={class_prefix}Model)
'''
    )

    print(f"created module: application/modules/{name}")
    print("next:")
    print(f"  1) include router in application/apis.py")
    print(f"  2) export model in application/models/__init__.py")
    print(f"  3) make revision m='add {name}' && make migrate")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/new_module.py <name>")
    main(sys.argv[1])
