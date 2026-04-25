"""FastAPI application entrypoint for the image CDN"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import DEBUG, HOST, PORT
from src.response import make_response
from src.routers import cdn
from src.services.image_cache import ensure_cache_dir
from src.utils.logging import setup_logging

UPSTREAM_TIMEOUT_SECONDS: float = 30.0


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage shared resources for the app lifecycle

    Creates the on-disk cache directory and a single ``httpx.AsyncClient``
    that is reused across all requests.
    """
    setup_logging(DEBUG)
    logger = logging.getLogger(__name__)

    ensure_cache_dir()
    timeout = httpx.Timeout(UPSTREAM_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http = client
        logger.info("[OK] img-cdn started (debug=%s)", DEBUG)
        yield
        logger.info("[OK] img-cdn shutting down")


app = FastAPI(
    title="img-cdn",
    description="Ekonomi image CDN proxy",
    version="0.2.0",
    debug=DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    return make_response(exc.status_code, exc.detail)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return make_response(422, "Validation error", exc.errors())


@app.exception_handler(Exception)
async def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).exception("Unhandled exception while serving %s", request.url.path)
    return make_response(500, "Internal server error")


app.include_router(cdn.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=DEBUG)
