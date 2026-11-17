import logging
import os


def configure_logging() -> None:
    configured_level = logging.getLevelName(os.getenv("LOG_LEVEL", "INFO").upper())
    level = configured_level if isinstance(configured_level, int) else logging.INFO

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if root_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    root_logger.addHandler(handler)
