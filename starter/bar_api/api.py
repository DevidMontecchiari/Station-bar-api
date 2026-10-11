"""Order exercise: supplied reads, then the one handler you complete."""
# Rusty Python? Read the small example in starter/README.md first.
# Start with the supplied GET handlers (2); edit only the marked task in (3).
# Setup (1) is supplied: revisit it when tracing how the service reaches a handler.
# From the repository root: python check.py starter (2 pass / 2 fail initially).
# Imports make names from other modules available here. A leading dot means
# another module in this package: .models refers to bar_api/models.py.
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Path as PathParameter, Request, Response
from .errors import ERROR_RESPONSES, install_error_handlers
from .models import MenuItem, Order, OrderInput
from .service import BarService
from .storage import JsonStore

# A URL ID must be an integer >= 1, e.g. the 1 in /orders/1.
RecordId = Annotated[int, PathParameter(ge=1)]


# 1. Supplied setup: create the app and connect its parts at startup.
# def defines a function; calling it runs its indented body.
# data_file: Path and -> FastAPI are input and return type hints.
def create_app(data_file: Path) -> FastAPI:
    app = FastAPI(title="Station Bar - order exercise", responses=ERROR_RESPONSES)
    install_error_handlers(app)  # Supplied HTTP error handling; no edits needed.
    # JsonStore handles the file; BarService applies the order rules.
    # ClassName(...) creates an object; = stores a value and . accesses an attribute.
    # Store this configured service on the app so handlers can use it.
    app.state.service = BarService(JsonStore(data_file))

    def get_service(request: Request) -> BarService:
        return request.app.state.service

    # Annotated combines a type with extra instructions for FastAPI.
    # Depends gets the function WITHOUT (): FastAPI calls it for us.
    # A collaborator is an object we use to do work: here, this app's BarService.
    Service = Annotated[BarService, Depends(get_service)]

    # 2. Supplied GET handlers: use these to understand the request flow.
    # @ introduces a decorator: here FastAPI registers the function for GET + path.
    # response_model describes and validates the returned data.
    @app.get("/menu-items/{menu_item_id}", response_model=MenuItem)
    def read_menu_item(menu_item_id: RecordId, service: Service):
        # menu_item_id is a value from the URL; service is supplied by FastAPI.
        # service.get_record(...) calls a method (a function on an object).
        # return gives its result back to FastAPI, which sends the JSON response.
        return service.get_record("menu_items", menu_item_id)

    @app.get("/orders", response_model=list[Order])
    def list_orders(service: Service):
        return service.list_records("orders")  # A collection, possibly empty.

    @app.get("/orders/{order_id}", response_model=Order)
    def read_order(order_id: RecordId, service: Service):
        return service.get_record("orders", order_id)  # One order by its ID.

    # 3. Your task: connect validated input to the supplied service.
    # body: request JSON parsed and validated against OrderInput.
    # response: lets you set response headers; service: the supplied collaborator.
    @app.post("/orders", response_model=Order, status_code=201)
    def create_order(body: OrderInput, response: Response, service: Service):
        # BEGIN CREATE ORDER EXERCISE
        # Replace the 501 placeholder with these three steps. Keep the same indentation:
        # 1. Call service.create_order using body.model_dump() (a dictionary).
        #    Keep the returned order: the service assigns its ID and saves it.
        # 2. Set response.headers["Location"] to /orders/<the returned ID>.
        #    order["id"] reads a dictionary value; f"...{value}..." inserts a value into text.
        # 3. Return that order. The decorator already specifies status 201.
        # The handler does not assign IDs/status or write the JSON file itself.
        # raise stops normal execution with an exception: replace this line.
        raise HTTPException(status_code=501, detail="Implement the create_order handler.")
        # END CREATE ORDER EXERCISE

    return app

# Check again: python check.py starter -> expect 4 passed.
# Then use /docs on port 8001: POST an order, GET its ID, try quantity 0.
# Full instructions and sample request: exercises/02-create-order.md.
