import logging
import uuid
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)


async def request_id_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


async def logging_middleware(request: Request, call_next: Callable):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info(f"{request.method} {request.url.path} rid={request_id}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} rid={request_id}")
    response.headers["X-Request-ID"] = request_id
    return response