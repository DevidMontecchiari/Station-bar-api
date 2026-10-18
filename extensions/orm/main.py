"""Read this first: familiar HTTP routes now receive a database session."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from database import initialise, make_engine
from models import AvailabilityInput, MenuItem, OrderInput, OrderOutput
from service import create_order, delete_order, read_order


def create_app(database_file: Path, *, echo: bool = False) -> FastAPI:
    engine = make_engine(database_file, echo=echo)

    @asynccontextmanager
    async def lifespan(_app):
        initialise(engine)
        yield
        engine.dispose()

    app = FastAPI(title="Station Bar: optional SQLite and ORM example", lifespan=lifespan)
    app.state.engine = engine  # Also used by the supplied tests.

    def get_session():
        with Session(engine) as session:
            yield session  # FastAPI supplies this collaborator; the context closes it.

    DatabaseSession = Annotated[Session, Depends(get_session)]

    @app.get("/menu-items", response_model=list[MenuItem])
    def list_menu(session: DatabaseSession):
        return session.exec(select(MenuItem).order_by(MenuItem.id)).all()

    @app.get("/orders/{order_id}", response_model=OrderOutput)
    def get_order(order_id: int, session: DatabaseSession):
        return read_order(session, order_id)

    @app.post("/orders", response_model=OrderOutput, status_code=201)
    def post_order(payload: OrderInput, response: Response, session: DatabaseSession):
        try:
            result = create_order(session, payload)
        except IntegrityError as error:
            raise HTTPException(409, "Order could not be stored consistently") from error
        response.headers["Location"] = f"/orders/{result.id}"
        return result

    @app.patch("/menu-items/{menu_item_id}", response_model=MenuItem)
    def change_availability(menu_item_id: int, payload: AvailabilityInput, session: DatabaseSession):
        item = session.get(MenuItem, menu_item_id)
        if item is None:
            raise HTTPException(404, "Menu item not found")
        item.available = payload.available
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @app.delete("/orders/{order_id}", status_code=204)
    def remove_order(order_id: int, session: DatabaseSession):
        delete_order(session, order_id)
        return Response(status_code=204)

    return app


app = create_app(Path(os.environ.get("BAR_ORM_DB", Path(__file__).parent / "data" / "bar.sqlite")),
                 echo=os.environ.get("BAR_SQL_ECHO") == "1")
