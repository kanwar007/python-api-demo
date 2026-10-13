import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("python_api_demo")
    logger.setLevel(settings.log_level.upper())
    logger.propagate = False

    if logger.handlers:
        return logger

    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        ),
    ]
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = configure_logger()