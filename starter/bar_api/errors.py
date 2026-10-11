"""Supplied HTTP error responses for the exercise; no student edits needed."""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from .models import Error
from .service import BarError

ERROR_RESPONSES = {
    404: {"model": Error, "description": "Resource not found"},
    422: {"model": Error, "description": "Invalid input or unavailable menu item"},
}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(BarError)
    async def business_error(request: Request, error: BarError):
        status = {"invalid_input": 422, "not_found": 404}[error.code]
        return JSONResponse(status_code=status, content={"code": error.code, "message": error.message})

    @app.exception_handler(RequestValidationError)
    async def input_error(request: Request, error: RequestValidationError):
        messages = [".".join(str(part) for part in e["loc"]) + ": " + e["msg"] for e in error.errors()]
        return JSONResponse(status_code=422, content={"code": "invalid_input", "message": "; ".join(messages)})

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        code = {404: "not_found", 405: "method_not_allowed", 501: "not_implemented"}.get(error.status_code, "http_error")
        return JSONResponse(status_code=error.status_code, headers=error.headers,
                            content={"code": code, "message": str(error.detail)})
