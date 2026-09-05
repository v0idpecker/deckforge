import json
import logging
import logging.config
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
task_id_var: ContextVar[str] = ContextVar("task_id", default="")


def set_request_id(value: str) -> None:
    request_id_var.set(value)


def set_task_id(value: str) -> None:
    task_id_var.set(value)


def get_record_context(record: logging.LogRecord) -> dict:
    context = {}
    if request_id := request_id_var.get():
        context["request_id"] = request_id
    if task_id := task_id_var.get():
        context["task_id"] = task_id
    return context


class ContextTextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        context = get_record_context(record)
        if not context:
            return base
        suffix = " ".join(f"{key}={value}" for key, value in context.items())
        return f"{base} [{suffix}]"


class ContextJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        payload.update(get_record_context(record))

        return json.dumps(payload, ensure_ascii=False)


VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _normalize_level(level: str) -> str:
    normalized = level.upper()
    if normalized not in VALID_LOG_LEVELS:
        return "INFO"
    return normalized


def setup_logging(level: str = "INFO", fmt: str = "text") -> None:
    fmt = fmt if fmt in {"text", "json"} else "text"

    logging.config.dictConfig(
        {
            "version": 1,
            # Важно: uvicorn, faststream и sqlalchemy конфигурируют свои
            # логгеры сами — не выключаем их.
            "disable_existing_loggers": False,
            "formatters": {
                "text": {
                    "()": "deckforge.logging_setup.ContextTextFormatter",
                    "fmt": "%(asctime)s %(levelname)-8s %(name)s: %(message)s",
                },
                "json": {
                    "()": "deckforge.logging_setup.ContextJsonFormatter",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": fmt,
                },
            },
            "loggers": {
                # SQL-стейтменты в логи не пишем даже на INFO,
                # при необходимости включается через LOG_LEVEL=DEBUG
                # в связке с этим ключом.
                "sqlalchemy.engine": {"level": "WARNING"},
            },
            "root": {
                "level": _normalize_level(level),
                "handlers": ["default"],
            },
        }
    )
