# -*- coding: utf-8 -*-
"""Unified loguru configuration."""

from __future__ import annotations

import os
import sys

from loguru import logger as loguru_logger

from conf import settings


class LoggingConfig:
    def __init__(self) -> None:
        self.debug = settings.DEBUG
        self.level = "DEBUG" if self.debug else "INFO"
        self.log_dir = settings.LOGS_ROOT
        self.ensure_log_dir()

    def ensure_log_dir(self) -> None:
        os.makedirs(self.log_dir, exist_ok=True)

    def get_log_format(self) -> str:
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )

    def get_file_format(self) -> str:
        return (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )

    def setup_logger(self):
        loguru_logger.remove()
        loguru_logger.add(
            sink=sys.stdout,
            level=self.level,
            format=self.get_log_format(),
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
        loguru_logger.add(
            sink=f"{self.log_dir}/app_{{time:YYYY-MM-DD}}.log",
            level="DEBUG",
            format=self.get_file_format(),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
        )
        loguru_logger.add(
            sink=f"{self.log_dir}/app_error_{{time:YYYY-MM-DD}}.log",
            level="ERROR",
            format=self.get_file_format(),
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            encoding="utf-8",
        )
        loguru_logger.info("Logger started")
        return loguru_logger


logging_config = LoggingConfig()
logger = logging_config.setup_logger()
