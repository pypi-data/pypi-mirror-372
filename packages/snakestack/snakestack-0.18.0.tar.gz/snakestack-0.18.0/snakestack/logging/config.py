import logging
import logging.config
from typing import Any

from snakestack.config import settings

DEFAULT_FILTERS: dict[str, Any] = {
    "request_id": {"()": "snakestack.logging.filters.RequestIdFilter"},
    "excluded_name": {
        "()": "snakestack.logging.filters.ExcludeLoggerFilter",
        "excluded_name": settings.snakestack_log_filter_excluded_name
    }
}


DEFAULT_HANDLERS: dict[str, Any] = {
    "console": {
        "class": "logging.StreamHandler",
        "formatter": settings.snakestack_log_default_formatter,
        "filters": settings.snakestack_log_default_filters.split(","),
    }
}


DEFAULT_FORMATTERS: dict[str, Any] = {
    "default": {
        "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    },
    "with_request_id": {
        "format": (
            "%(asctime)s [%(levelname)s] [req_id=%(request_id)s] "
            "%(name)s: %(message)s"
        )
    },
    "custom_json": {
        "()": "snakestack.logging.formatters.JsonFormatter"
    }
}

DEFAULT_LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": DEFAULT_FORMATTERS,
    "handlers": DEFAULT_HANDLERS,
    "filters": DEFAULT_FILTERS,
    "root": {
        "level": settings.snakestack_log_level,
        "handlers": ["console"]
    }
}


def setup_logging(logging_config: dict[str, Any] | None = None) -> None:
    logging.config.dictConfig(logging_config or DEFAULT_LOGGING_CONFIG)
