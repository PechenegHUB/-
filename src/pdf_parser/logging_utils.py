"""Logging helpers for the project."""

from __future__ import annotations

import logging


LOGGER_NAME = "pdf_parser"


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a project logger instance."""
    return logging.getLogger(LOGGER_NAME if name is None else f"{LOGGER_NAME}.{name}")
