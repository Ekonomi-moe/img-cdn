"""Project configuration loader

Loads runtime settings from a project-root ``.env`` file via ``python-dotenv``.
Missing keys fall back to sensible defaults; ``API_URL`` is required.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


def _env_bool(name: str, default: bool) -> bool:
    """Parse a boolean environment variable

    Args:
        name(str): Environment variable name
        default(bool): Value used when the variable is unset

    Return:
        value(bool): Parsed boolean
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _require_env(name: str) -> str:
    """Read a required environment variable or raise

    Args:
        name(str): Environment variable name

    Return:
        value(str): The non-empty environment value
    """
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DEBUG: bool = _env_bool("DEBUG", False)
HOST: str = os.environ.get("HOST", "0.0.0.0")
PORT: int = int(os.environ.get("PORT", "5000"))
API_URL: str = _require_env("API_URL").rstrip("/")
