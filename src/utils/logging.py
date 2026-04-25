"""Logging setup backed by prompt_toolkit

Provides a logging handler that emits records via
``prompt_toolkit.shortcuts.print_formatted_text`` with ANSI styling, falling
back to plain text when stderr is not attached to a TTY (e.g. systemd journal,
serial console, mod_wsgi-style log capture).
"""

import logging
import sys
from typing import Optional

from prompt_toolkit.formatted_text import ANSI, FormattedText
from prompt_toolkit.shortcuts import print_formatted_text

INFO_FORMAT: str = "[%(asctime)s] %(levelname)s # %(message)s"
DEBUG_FORMAT: str = "[%(asctime)s] [%(filename)s:%(lineno)d] %(levelname)s # %(message)s"

LEVEL_STYLES: dict[int, str] = {
    logging.DEBUG: "ansibrightblack",
    logging.INFO: "ansicyan",
    logging.WARNING: "ansiyellow",
    logging.ERROR: "ansired",
    logging.CRITICAL: "ansibrightred bold",
}


class PromptToolkitHandler(logging.Handler):
    """logging.Handler that renders through prompt_toolkit"""

    def __init__(self, use_style: bool) -> None:
        super().__init__()
        self.use_style = use_style

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            if self.use_style:
                style = LEVEL_STYLES.get(record.levelno, "")
                print_formatted_text(FormattedText([(style, message)]))
            else:
                print_formatted_text(ANSI(message))
        except Exception:
            self.handleError(record)


def _is_tty() -> bool:
    stream = sys.stderr
    return hasattr(stream, "isatty") and stream.isatty()


def setup_logging(debug: bool, logger_name: Optional[str] = None) -> logging.Logger:
    """Configure the root (or named) logger to emit through prompt_toolkit

    Args:
        debug(bool): Enable DEBUG level and the verbose log format
        logger_name(str, optional): Logger to configure. ``None`` configures the root logger.

    Return:
        logger(logging.Logger): The configured logger instance
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)

    for existing in list(logger.handlers):
        logger.removeHandler(existing)

    handler = PromptToolkitHandler(use_style=_is_tty())
    fmt = DEBUG_FORMAT if debug else INFO_FORMAT
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
