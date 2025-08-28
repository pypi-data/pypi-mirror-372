import logging
import sys
from pathlib import Path

import environ
from loguru import logger

env = environ.Env()

DEBUG = env.bool("RORI_DEBUG", default=False)

DEFAULT_RORI_DIR = Path.home() / ".rori"
RORI_DIR = Path(env.path("RORI_DIR", default=DEFAULT_RORI_DIR))

COLOR_MAIN = "#fdca40"
COLOR_ACCENT = "#3aaed8"
# COLOR_ACCENT = "#d75fd7"  # orchid
COLOR_ERROR = "#f64740"

ICON_RORI = "🚥"
ICON_RORIV = "🚦"
ICON_INFO = "💡"
ICON_ERROR = "🍄‍🟫"
ICON_MULTI_ERROR = "🍄"
ICON_STATUS = "•"

DATETIME_FORMAT = "%H:%M:%S %Y/%m/%d"

# watcher settings
# TODO: enable by default once ready
RORIW_ENABLED = env.bool("RORIW_ENABLED", default=False)
RORIW_MAX_FAILS = env.int("RORIW_MAX_FAILS", default=5)
RORIW_CONCURRENCY = env.int("RORIW_CONCURRENCY", default=10)
RORIW_INTERVAL = env.int("RORIW_INTERVAL", default=30)
RORIW_EXEC = "rori-watcher"

logger.remove()
if DEBUG:
    logger.add(sys.stderr, level=logging.DEBUG)
