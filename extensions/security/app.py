"""Protected subset of the bar API; reuses the existing service and JSON store."""
from pathlib import Path
import sys
from typing import Annotated
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "solution"))
from bar_api.models import MenuItem, MenuItemInput
from bar_api.service import BarError, BarService
from bar_api.storage import JsonStore
from .auth import Principal, TokenRegistry, User, require_staff

Staff = Annotated[Principal, Depends(require_staff)]


def create_app(data_file: Path, tokens: TokenRegistry, accounts=None, secure_cookies=False) -> FastAPI:
    app = FastAPI(title="Station Bar | Security: identity and permission", version="1.0",
                  description="Classroom subset on port 8003. Public menu; staff-only creation. "
                  "Browser login uses server sessions; this API uses separate opaque bearer tokens.")
    app.state.tokens = tokens
    app.state.service = BarService(JsonStore(data_file))

    @app.exception_handler(BarError)
    async def business_error(request: Request, error: BarError):
        return JSONResponse(status_code={"not_found": 404, "invalid_input": 422, "conflict": 409}[error.code],
                            content={"code": error.code, "message": error.message})

    @app.get("/menu-items", response_model=list[MenuItem], tags=["Public"])
    def menu():
        return app.state.service.list_records("menu_items")

    @app.get("/menu-items/{item_id}", response_model=MenuItem, tags=["Public"])
    def menu_item(item_id: int):
        return app.state.service.get_record("menu_items", item_id)

    @app.get("/whoami", tags=["Verified identity"], responses={401: {"description": "No valid credential"}})
    def whoami(user: User):
        return {"username": user.username, "permissions": sorted(user.permissions)}

    @app.post("/menu-items", response_model=MenuItem, status_code=201, tags=["Staff operation"],
              responses={401: {"description": "No valid credential"},
                         403: {"description": "Identity lacks menu:write"}})
    def create_menu_item(body: MenuItemInput, response: Response, user: Staff):
        # FastAPI resolves the user and staff dependency before this function runs.
        item = app.state.service.create_menu_item(body.model_dump())
        response.headers["Location"] = f"/menu-items/{item['id']}"
        return item

    # No unprotected parent API is mounted; it would expose alternative writes.
    # This example protects menu creation; it does not claim order ownership.
    if accounts is not None:
        from .pages import install_pages
        install_pages(app, accounts, secure_cookies)
    return app
