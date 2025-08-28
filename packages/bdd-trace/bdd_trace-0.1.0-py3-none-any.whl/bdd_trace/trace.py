import logging
import os
from enum import Enum

from opentelemetry.instrumentation import auto_instrumentation
from opentelemetry.sdk._logs import LoggingHandler


class Profile(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


TRACES_EXPORTER_KEY = "traces_exporter"
METRICS_EXPORTER_KEY = "metrics_exporter"
LOGS_EXPORTER_KEY = "logs_exporter"
EXPORTER_OTLP_ENDPOINT_KEY = "exporter_otlp_endpoint"
EXPORTER_OTLP_INSECURE_KEY = "exporter_otlp_insecure"
SERVICE_NAME_KEY = "service_name"
PYTHON_FASTAPI_EXCLUDE_URLS_KEY = "python_fastapi_exclude_urls"
INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST_KEY = "instrumentation_http_capture_headers_server_request"

default_envs = {
    TRACES_EXPORTER_KEY: "otlp",
    METRICS_EXPORTER_KEY: "otlp",
    LOGS_EXPORTER_KEY: "otlp",
    PYTHON_FASTAPI_EXCLUDE_URLS_KEY: "/healthCheck",
    INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST_KEY: "X-User-Id,X-Conversation-From",
    EXPORTER_OTLP_INSECURE_KEY: "true",
}

profile_config = {
    Profile.DEV: {
        TRACES_EXPORTER_KEY: "console",
        METRICS_EXPORTER_KEY: "console",
        LOGS_EXPORTER_KEY: "console",
        EXPORTER_OTLP_ENDPOINT_KEY: None,
    },
    Profile.TEST: {
        TRACES_EXPORTER_KEY: "otlp",
        METRICS_EXPORTER_KEY: "otlp",
        LOGS_EXPORTER_KEY: "otlp",
        EXPORTER_OTLP_ENDPOINT_KEY: "http://otel-sls-collector:4317",
    },
    Profile.PROD: {
        TRACES_EXPORTER_KEY: "otlp",
        METRICS_EXPORTER_KEY: "otlp",
        LOGS_EXPORTER_KEY: "otlp",
        EXPORTER_OTLP_ENDPOINT_KEY: "http://otel-sls-collector:4317",
    },
}

logger = logging.getLogger(__name__)


def init_trace(
    *,
    service_name: str | None = None,
    profile: Profile | None = None,
    exporter_otlp_endpoint: str | None = None,
    **kwargs,
) -> None:
    # 设置环境变量，优先级：环境变量 > 参数 > profile 配置 > 默认配置
    for key, value in kwargs.items():
        _set_env(key, value)

    if profile:
        for key, value in profile_config[profile].items():
            _set_env(key, value)
    elif exporter_otlp_endpoint:
        _set_env(EXPORTER_OTLP_ENDPOINT_KEY, exporter_otlp_endpoint)
    else:
        raise ValueError("either profile or exporter_otlp_endpoint is required")

    if service_name:
        _set_env(SERVICE_NAME_KEY, service_name)
    elif _get_env(SERVICE_NAME_KEY) is None:
        raise ValueError("service_name is required")

    for key, value in default_envs.items():
        _set_env(key, value)

    auto_instrumentation.initialize()

    _setup_logger_handler()


def _set_env(key: str, value: str | None) -> None:
    if value is None:
        return

    env_key = _convert_to_env_key(key)
    if existing_value := os.getenv(env_key):
        logger.info(f"existing env {env_key}={existing_value}")
    else:
        logger.debug(f"set env {env_key}={value}")
        os.environ[env_key] = value


def _get_env(key: str) -> str | None:
    env_key = _convert_to_env_key(key)
    return os.getenv(env_key)


def _convert_to_env_key(key: str) -> str:
    return f"OTEL_{key.upper()}"


def _setup_logger_handler() -> None:
    otel_handler = LoggingHandler()
    logging.getLogger().addHandler(otel_handler)
