"""CDN image-serving router"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, Response

from src.response import make_response
from src.services.image_cache import resolve_image

SPECIAL_ALLOW: str = "ekonomi.png"
MIN_PATH_LEN: int = 64

router = APIRouter(tags=["CDN"])


@router.get(
    "/{path:path}",
    response_class=Response,
    responses={
        200: {
            "description": "Image bytes streamed back to the client",
            "content": {"image/png": {}},
        },
        404: {
            "description": "Path is invalid or the image is not registered upstream",
            "content": {
                "application/json": {
                    "examples": {
                        "short_path": {
                            "summary": "Path too short and not the special allow-listed name",
                            "value": {
                                "status": 404,
                                "message": "Not Found",
                                "data": None,
                            },
                        },
                        "unknown_image": {
                            "summary": "Image id is not present in the upstream list",
                            "value": {
                                "status": 404,
                                "message": "Image not found",
                                "data": None,
                            },
                        },
                    }
                }
            },
        },
        502: {
            "description": "Upstream API returned a non-200 status when fetching the image",
            "content": {
                "application/json": {
                    "examples": {
                        "upstream_error": {
                            "summary": "Pass-through of upstream status",
                            "value": {
                                "status": 502,
                                "message": "Server-side request error",
                                "data": None,
                            },
                        }
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error",
            "content": {
                "application/json": {
                    "examples": {
                        "internal_error": {
                            "summary": "Caught by the global exception handler",
                            "value": {
                                "status": 500,
                                "message": "Internal server error",
                                "data": None,
                            },
                        }
                    }
                }
            },
        },
    },
)
async def get_image(path: str, request: Request) -> Response:
    """Serve a cached image by id, fetching from the upstream API on first hit

    Args:
        path(str): Path component such as ``<id>.png`` or the special ``ekonomi.png``
        request(fastapi.Request): Incoming request (used to access the shared httpx client)

    Return:
        response(Response): ``FileResponse`` on success, otherwise an error envelope ``JSONResponse``
    """
    if len(path) < MIN_PATH_LEN and path != SPECIAL_ALLOW:
        return make_response(404, "Not Found")

    img_id = path.split(".")[0]
    client = request.app.state.http
    result = await resolve_image(client, img_id)

    if isinstance(result, Path):
        return FileResponse(result, media_type="image/png")

    status, message = result
    return make_response(status, message)
