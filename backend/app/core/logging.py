"""Centralized application logging configuration.

Provides:
- Structured (JSON) console logging by default
- Optional CloudWatch Logs shipping via watchtower when enabled
- Request-scoped context (request_id) via contextvars + logging filter
"""

from __future__ import annotations

import contextvars
import json
import logging
import logging.config
import os
import socket
import traceback
from datetime import datetime, timezone
from typing import Any


request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def set_request_id(request_id: str) -> contextvars.Token[str | None]:
    return request_id_var.set(request_id)


def reset_request_id(token: contextvars.Token[str | None]) -> None:
    request_id_var.reset(token)


def get_request_id() -> str | None:
    return request_id_var.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.request_id = get_request_id() or "-"
        return True


class JsonFormatter(logging.Formatter):
    _RESERVED: set[str] = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
        "request_id",
    }

    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()

        payload: dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "request_id": getattr(record, "request_id", "-"),
        }

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self._RESERVED and not key.startswith("_")
        }
        if extras:
            payload.update(extras)

        if record.exc_info:
            payload["exception"] = "".join(traceback.format_exception(*record.exc_info))
        elif record.exc_text:
            payload["exception"] = record.exc_text

        return json.dumps(payload, default=str, ensure_ascii=False)


def _configure_stdlib_logging(log_level: str, log_format: str) -> None:
    # Configure root + key loggers to propagate to root so we only attach handlers once.
    handler_name = "console"
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
            },
            "json": {"()": "app.core.logging.JsonFormatter"},
        },
        "filters": {
            "request_id": {"()": "app.core.logging.RequestIdFilter"},
        },
        "handlers": {
            handler_name: {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "plain" if log_format.lower() == "plain" else "json",
                "filters": ["request_id"],
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": log_level, "handlers": [handler_name]},
        "loggers": {
            # Normalize common app/server loggers.
            "uvicorn": {"level": log_level, "handlers": [], "propagate": True},
            "uvicorn.error": {"level": log_level, "handlers": [], "propagate": True},
            # Avoid double access logs; our middleware emits one per request.
            "uvicorn.access": {"level": "WARNING", "handlers": [], "propagate": True},
            "fastapi": {"level": log_level, "handlers": [], "propagate": True},
        },
    }

    logging.config.dictConfig(config)


def _validate_cloudwatch_settings(settings: Any) -> None:
    missing: list[str] = []
    if not getattr(settings, "AWS_REGION", None):
        missing.append("AWS_REGION")
    if not getattr(settings, "CLOUDWATCH_LOG_GROUP", None):
        missing.append("CLOUDWATCH_LOG_GROUP")
    if missing:
        raise RuntimeError(
            "CloudWatch logging enabled but missing required settings: "
            + ", ".join(missing)
        )


def _default_log_stream_name(settings: Any) -> str:
    service = getattr(settings, "LOG_SERVICE_NAME", "service")
    env = getattr(settings, "ENV", "unknown")
    host = socket.gethostname()
    pid = os.getpid()
    return f"{service}/{env}/{host}/{pid}"


def _create_cloudwatch_handler(*, settings: Any, session: Any, watchtower: Any) -> Any:
    """
    Create a CloudWatch handler across watchtower version differences.

    Some watchtower versions don't accept `boto3_session=...`.
    """
    stream_name = settings.CLOUDWATCH_LOG_STREAM or _default_log_stream_name(settings)

    # Try common parameter names across versions.
    base_kwargs_candidates: list[dict[str, Any]] = [
        {
            "log_group": settings.CLOUDWATCH_LOG_GROUP,
            "stream_name": stream_name,
            "create_log_group": False,
        },
        {
            "log_group_name": settings.CLOUDWATCH_LOG_GROUP,
            "stream_name": stream_name,
            "create_log_group": False,
        },
    ]

    for base_kwargs in base_kwargs_candidates:
        try:
            return watchtower.CloudWatchLogHandler(boto3_session=session, **base_kwargs)
        except TypeError:
            pass

        try:
            client = session.client("logs")
            return watchtower.CloudWatchLogHandler(boto3_client=client, **base_kwargs)
        except TypeError:
            pass

        try:
            return watchtower.CloudWatchLogHandler(**base_kwargs)
        except TypeError:
            pass

    raise TypeError(
        "Unable to initialize watchtower CloudWatchLogHandler with this watchtower version."
    )


def setup_logging(settings: Any) -> logging.Handler | None:
    """
    Configure application logging.

    Returns the CloudWatch handler (if enabled), so the caller can close it on shutdown.
    """
    log_level = str(getattr(settings, "LOG_LEVEL", "INFO")).upper()
    log_format = str(getattr(settings, "LOG_FORMAT", "json")).lower()

    _configure_stdlib_logging(log_level=log_level, log_format=log_format)

    if not getattr(settings, "CLOUDWATCH_ENABLED", False):
        return None

    try:
        _validate_cloudwatch_settings(settings)
    except Exception:
        # Ensure the error is visible even if logging isn't fully configured upstream.
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception("cloudwatch_logging_config_invalid")
        raise

    try:
        import boto3  # type: ignore
        import watchtower  # type: ignore
    except Exception:
        logging.getLogger(__name__).exception(
            "cloudwatch_logging_dependencies_missing",
            extra={"event": "cloudwatch_logging_dependencies_missing"},
        )
        raise

    session = boto3.session.Session(region_name=settings.AWS_REGION)
    cloudwatch_handler = _create_cloudwatch_handler(
        settings=settings, session=session, watchtower=watchtower
    )
    cloudwatch_handler.setLevel(log_level)
    cloudwatch_handler.addFilter(RequestIdFilter())

    # Match formatter to console handler for consistent structure.
    if log_format == "plain":
        cloudwatch_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
            )
        )
    else:
        cloudwatch_handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.addHandler(cloudwatch_handler)

    return cloudwatch_handler
