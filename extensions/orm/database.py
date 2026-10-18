"""Provided setup: one engine per app, one short-lived session per request."""
import json
from pathlib import Path
from sqlalchemy import event, inspect
from sqlmodel import Session, SQLModel, create_engine
from models import BarOrder, MenuItem, OrderLine


def make_engine(database_file: Path, *, echo: bool = False):
    database_file.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        "sqlite:///" + database_file.resolve().as_posix(),
        connect_args={"check_same_thread": False}, echo=echo,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        # SQLite must enable FK enforcement on each connection.
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def initialise(engine):
    # Seed only a new schema. An emptied existing table must stay empty on restart.
    new_schema = not inspect(engine).has_table("menu_item")
    SQLModel.metadata.create_all(engine)
    if not new_schema:
        return
    seed = json.loads(Path(__file__).with_name("seed.json").read_text(encoding="utf-8"))
    with Session(engine) as session, session.begin():
        session.add_all(MenuItem(**row) for row in seed["menu_items"])
        session.flush()  # Menu rows must exist before their foreign keys are used.
        for source in seed["orders"]:
            order = BarOrder(id=source["id"], table_number=source["table"], status=source["status"])
            session.add(order)
            session.flush()
            session.add_all(OrderLine(order_id=order.id, **line) for line in source["items"])
    # The context commits together on success and rolls back on failure.
    # create_all is convenient for a fresh demo, not a schema migration tool.
