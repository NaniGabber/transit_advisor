import logging
import os

from dotenv import load_dotenv

load_dotenv()

_configured_level = os.getenv("LOG_LEVEL", "ERROR").strip().upper()
LOG_LEVEL = logging.getLevelNamesMapping().get(_configured_level, logging.ERROR)
