import math
from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _json_safe(value: Any) -> Any:
    # inf / nan can't be written as JSON, so show them as text ("inf")
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


async def request_validation_error_handler(request: Request, error: RequestValidationError) -> JSONResponse:
    # Same 422 body as FastAPI's default, but it doesn't crash (500) when the
    # rejected input is inf or nan, e.g. a price of 1e999.
    return JSONResponse(
        status_code=422,
        content={"detail": _json_safe(jsonable_encoder(error.errors()))},
    )
