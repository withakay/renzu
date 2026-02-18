"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any

from pythonjsonlogger.json import JsonFormatter


class CustomJsonFormatter(JsonFormatter):
    """Custom JSON formatter with additional fields."""

    def add_fields(
        self,
        log_data: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_data, record, message_dict)
        log_data["level"] = record.levelname
        log_data["logger"] = record.name
        for attr in ("method", "path", "status_code", "duration_ms", "correlation_id"):
            value = getattr(record, attr, None)
            if value is not None:
                log_data[attr] = value


def setup_logging(level: str = "INFO") -> None:
    """Configure structured JSON logging."""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        rename_fields={"levelname": "level", "name": "logger"},
    )
    log_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level.upper())
    root_logger.handlers = [log_handler]
