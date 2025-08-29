from __future__ import annotations
import logging
import json
import sys
from typing import Optional
from .config import LogConfig


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(config: LogConfig, logger_name: Optional[str] = None) -> logging.Logger:
    level = getattr(logging, config.level.upper(), logging.INFO)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Remove existing handlers to allow reconfiguration
    for h in list(logger.handlers):
        logger.removeHandler(h)

    if config.destination and config.destination != "stdout":
        handler: logging.Handler = logging.FileHandler(config.destination)
    else:
        handler = logging.StreamHandler(sys.stdout)

    if config.json_enabled:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

    logger.addHandler(handler)
    return logger


