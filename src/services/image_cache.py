"""Image fetch + on-disk cache orchestration"""

import logging
from pathlib import Path
from typing import Union

import httpx

from src.config import API_URL, PROJECT_ROOT

logger = logging.getLogger(__name__)

CACHE_DIR: Path = PROJECT_ROOT / "cache"


def ensure_cache_dir() -> None:
    """Create the cache directory if missing"""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)


def cache_path_for(img_id: str) -> Path:
    """Return the on-disk cache path for an image id

    Args:
        img_id(str): Image identifier (no extension)

    Return:
        path(pathlib.Path): Absolute path to the cached PNG (may not exist yet)
    """
    return CACHE_DIR / f"{img_id}.png"


async def fetch_image_list(client: httpx.AsyncClient) -> list[str]:
    """Fetch the list of valid image ids from the upstream API

    Args:
        client(httpx.AsyncClient): Shared HTTP client

    Return:
        ids(list[str]): Allowed image identifiers
    """
    response = await client.get(f"{API_URL}/api/ddr_imglist")
    response.raise_for_status()
    payload = response.json()
    return list(payload.get("data", []))


async def fetch_image_bytes(
    client: httpx.AsyncClient, img_id: str
) -> tuple[int, bytes]:
    """Fetch a single image's bytes from the upstream API

    Args:
        client(httpx.AsyncClient): Shared HTTP client
        img_id(str): Image identifier

    Return:
        result(tuple[int, bytes]): Upstream HTTP status code and raw response body
    """
    response = await client.get(f"{API_URL}/api/ddr_img", params={"id": img_id})
    return response.status_code, response.content


async def resolve_image(
    client: httpx.AsyncClient, img_id: str
) -> Union[Path, tuple[int, str]]:
    """Resolve an image id to a cached file path or an error tuple

    Validates the id against the upstream list, returns a cached file when
    available, otherwise downloads and caches it. A stale local cache file is
    deleted when the id is no longer present upstream.

    Args:
        client(httpx.AsyncClient): Shared HTTP client
        img_id(str): Image identifier

    Return:
        result(Path | tuple[int, str]):
            On success: absolute path to the cached PNG.
            On failure: ``(status_code, message)`` tuple to be wrapped in the API envelope.
    """
    ensure_cache_dir()
    cache_file = cache_path_for(img_id)

    valid_ids = await fetch_image_list(client)

    if img_id not in valid_ids:
        if cache_file.exists():
            cache_file.unlink()
        return 404, "Image not found"

    if cache_file.exists():
        return cache_file

    status, body = await fetch_image_bytes(client, img_id)
    if status != 200:
        return status, "Server-side request error"

    cache_file.write_bytes(body)
    return cache_file
