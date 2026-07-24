# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from application.db.base import KeelModel
from conf import settings


class FileModel(KeelModel):
    __tablename__ = f"{settings.TABLE_PREFIX}file"

    file_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    upload_user_id: Mapped[int] = mapped_column(Integer, index=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
