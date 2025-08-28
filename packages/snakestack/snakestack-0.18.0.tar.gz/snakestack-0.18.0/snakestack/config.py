from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from snakestack import version


class SnakeStackSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    snakestack_log_level: str = Field(
        default="INFO",
        description="Logging level for the application (e.g., DEBUG, INFO, WARNING, ERROR)."
    )

    snakestack_log_default_formatter: str = Field(
        default="default",
        description="Default formatter to be used in the logging configuration (e.g., default, custom_json, with_request_id)."
    )

    snakestack_log_default_filters: str = Field(
        default="request_id",
        description="Comma-separated list of default filters to be applied to log records (e.g., request_id, excluded_name)."
    )

    snakestack_log_filter_excluded_name: list[str] | None = Field(
        default=None,
        description="Logger name or pattern to exclude from logging output (e.g., 'exclude.me' to suppress logs from that logger)."
    )

    snakestack_version: str = Field(
        default=version.__version__,
        description=""
    )

    snakestack_mongodb_url: str = Field(
        default="mongodb://localhost:27017",
        description=""
    )

    snakestack_mongodb_dbname: str = Field(
        default="snakestack",
        description=""
    )

    snakestack_otel_disabled: bool = Field(
        default=False,
        description=(
            "Disables only the OpenTelemetry instrumentation provided by the SnakeStack library. "
            "This allows external OpenTelemetry configurations (e.g., opentelemetry-bootstrap or custom distro) "
            "to take full control over instrumentation without duplication. "
            "Equivalent to setting the environment variable SNAKESTACK_OTEL_DISABLED=true."
        )
    )

    pubsub_project_id: str = Field(
        default="snakestack-project",
        description=""
    )

    otel_sdk_disabled: bool = Field(
        default=False,
        description=(
            "Disables the entire OpenTelemetry SDK, including all automatic and manual instrumentation. "
            "Equivalent to setting the environment variable OTEL_SDK_DISABLED=true. "
            "When enabled, no traces, metrics, or logs will be generated or exported by the OpenTelemetry SDK."
        )
    )

    @field_validator("snakestack_log_default_formatter")
    @classmethod
    def validate_log_formatter(cls, v: str) -> str:
        allowed = {"default", "custom_json", "with_request_id"}
        if v not in allowed:
            raise ValueError(f"Invalid formatter '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("snakestack_log_default_filters")
    @classmethod
    def validate_log_filter(cls, v: str) -> str:
        allowed = ["request_id", "excluded_name"]
        if not all([item in allowed for item in v.split(",")]):
            raise ValueError(f"Invalid filter '{v}'. Must be one of: {', '.join(allowed)}.")
        return v

    @field_validator("snakestack_log_filter_excluded_name", mode="before")
    @classmethod
    def _coerce_excluded_names(cls, v: Any) -> list[str]:
        if v is None or v == "":
            return []

        if isinstance(v, str):
            parts = [p.strip() for p in v.split(",")]
            return [p for p in parts if p]

        raise TypeError(
            "Invalid excluded name filter. Must be a comma-separated string"
        )

@lru_cache
def get_settings() -> SnakeStackSettings:
    return SnakeStackSettings()


settings = get_settings()
