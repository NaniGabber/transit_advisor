import logging
import os

from dotenv import load_dotenv

load_dotenv()

_configured_level = os.getenv("LOG_LEVEL", "ERROR").strip().upper()
LOG_LEVEL = logging.getLevelNamesMapping().get(_configured_level, logging.ERROR)


def _positive_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


def _boolean(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


RATE_LIMIT_REQUESTS = _positive_int("RATE_LIMIT_REQUESTS", 100)
RATE_LIMIT_WINDOW_SECONDS = _positive_int("RATE_LIMIT_WINDOW_SECONDS", 60)
RATE_LIMIT_TRUST_PROXY_HEADERS = _boolean("RATE_LIMIT_TRUST_PROXY_HEADERS", False)
