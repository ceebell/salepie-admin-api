# app/core/logging_config.py

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def get_log_dir():

    # ⭐ priority 1: ENV override
    env_dir = os.getenv("LOG_DIR")
    if env_dir:
        return Path(env_dir)

    # ⭐ priority 2: dev (uvicorn run)
    if os.getenv("ENV", "dev") == "dev":
        return Path("./log")

    # ⭐ priority 3: production default
    return Path("/var/log/salepie")


def setup_logging():

    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = TimedRotatingFileHandler(
        filename=str(log_dir / "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)
