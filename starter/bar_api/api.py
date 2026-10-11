"""HTTP boundary: parse input, call the service, map outcomes to HTTP."""
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, Path as PathParameter, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from .models import Error, MenuItem, MenuItemInput, Order, OrderInput
from .service import BarError, BarService
from .storage import JsonStore

RecordId = Annotated[int, PathParameter(ge=1)]
ERRORS = {
    404: {"model": Error, "description": "Resource not found"},
    409: {"model": Error, "description": "Conflict with current state"},
    422: {"model": Error, "description": "Invalid input or unavailable menu item"},
}
LOCATION = {"Location": {"description": "Relative URL of the created resource", "schema": {"type": "string"}}}

def create_app(data_file: Path) -> FastAPI:
    app = FastAPI(title="Station Bar API", version="0.2.1",
                  description="Local classroom implementation. Order status transitions are a later extension.")
    app.state.service = BarService(JsonStore(data_file))

    def get_service(request: Request) -> BarService:
        return request.app.state.service

    Service = Annotated[BarService, Depends(get_service)]

    @app.exception_handler(BarError)
    async def business_error(request: Request, error: BarError):
        status = {"invalid_input": 422, "not_found": 404, "conflict": 409}[error.code]
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

    @app.get("/menu-items", response_model=list[MenuItem], tags=["Menu items"], operation_id="listMenuItems")
    def list_menu_items(service: Service):
        return service.list_records("menu_items")

    @app.get("/menu-items/{menu_item_id}", response_model=MenuItem, tags=["Menu items"],
             operation_id="readMenuItem", responses={k: ERRORS[k] for k in (404, 422)})
    def read_menu_item(menu_item_id: RecordId, service: Service):
        return service.get_record("menu_items", menu_item_id)

    @app.post("/menu-items", response_model=MenuItem, status_code=201, tags=["Menu items"],
              operation_id="createMenuItem", responses={422: ERRORS[422], 201: {"headers": LOCATION}})
    def create_menu_item(body: MenuItemInput, response: Response, service: Service):
        item = service.create_menu_item(body.model_dump())
        response.headers["Location"] = f"/menu-items/{item['id']}"
        return item

    @app.put("/menu-items/{menu_item_id}", response_model=MenuItem, tags=["Menu items"],
             operation_id="replaceMenuItem", responses=ERRORS)
    def replace_menu_item(menu_item_id: RecordId, body: MenuItemInput, service: Service):
        return service.replace_menu_item(menu_item_id, body.model_dump())

    @app.delete("/menu-items/{menu_item_id}", status_code=204, response_class=Response, tags=["Menu items"],
                operation_id="deleteMenuItem", responses=ERRORS)
    def delete_menu_item(menu_item_id: RecordId, service: Service):
        service.delete_menu_item(menu_item_id)
        return Response(status_code=204)

    @app.get("/orders", response_model=list[Order], tags=["Orders"], operation_id="listOrders")
    def list_orders(service: Service):
        return service.list_records("orders")

    @app.get("/orders/{order_id}", response_model=Order, tags=["Orders"],
             operation_id="readOrder", responses={k: ERRORS[k] for k in (404, 422)})
    def read_order(order_id: RecordId, service: Service):
        return service.get_record("orders", order_id)

    @app.post("/orders", response_model=Order, status_code=201, tags=["Orders"],
              operation_id="createOrder", responses={422: ERRORS[422], 201: {"headers": LOCATION}})
    def create_order(body: OrderInput, response: Response, service: Service):
        # BEGIN CREATE ORDER EXERCISE
        # Use service.create_order(body.model_dump()), set Location, return the order.
        raise HTTPException(status_code=501, detail="Implement the create_order handler.")
        # END CREATE ORDER EXERCISE

    @app.put("/orders/{order_id}", response_model=Order, tags=["Orders"],
             operation_id="replaceOrder", responses=ERRORS)
    def replace_order(order_id: RecordId, body: OrderInput, service: Service):
        return service.replace_order(order_id, body.model_dump())

    @app.delete("/orders/{order_id}", status_code=204, response_class=Response, tags=["Orders"],
                operation_id="deleteOrder", responses=ERRORS)
    def delete_order(order_id: RecordId, service: Service):
        service.delete_order(order_id)
        return Response(status_code=204)

    return app
