"""Behavioural checks use temporary databases, never the classroom data."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from main import create_app
from models import BarOrder, MenuItem, OrderLine

PAYLOAD = {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}


@pytest.fixture
def running(tmp_path):
    app = create_app(tmp_path / "bar.sqlite")
    with TestClient(app) as client:
        yield app, client


def test_crud_and_nested_response(running):
    app, client = running
    assert len(client.get("/menu-items").json()) == 3
    response = client.post("/orders", json=PAYLOAD)
    assert response.status_code == 201
    order_id = response.json()["id"]
    assert response.headers["location"] == f"/orders/{order_id}"
    assert client.get(response.headers["location"]).json() == {**PAYLOAD, "id": order_id, "status": "pending"}
    assert client.patch("/menu-items/1", json={"available": False}).json()["available"] is False
    assert client.post("/orders", json=PAYLOAD).status_code == 409
    assert client.delete(f"/orders/{order_id}").status_code == 204
    assert client.get(f"/orders/{order_id}").status_code == 404
    with Session(app.state.engine) as session:
        assert session.exec(select(OrderLine)).all() == []


def test_restart_keeps_orders_and_availability(tmp_path):
    path = tmp_path / "bar.sqlite"
    with TestClient(create_app(path)) as client:
        response = client.post("/orders", json=PAYLOAD)
        location = response.headers["location"]
        client.patch("/menu-items/1", json={"available": False})
    with TestClient(create_app(path)) as client:
        assert client.get(location).json()["items"] == PAYLOAD["items"]
        assert client.get("/menu-items").json()[0]["available"] is False


def test_empty_existing_menu_is_not_reseeded(tmp_path):
    path = tmp_path / "bar.sqlite"
    app = create_app(path)
    with TestClient(app):
        with Session(app.state.engine) as session:
            for item in session.exec(select(MenuItem)).all():
                session.delete(item)
            session.commit()
    with TestClient(create_app(path)) as client:
        assert client.get("/menu-items").json() == []


@pytest.mark.parametrize("items,status", [
    ([{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 3, "quantity": 1}], 409),
    ([{"menu_item_id": 999, "quantity": 1}], 404),
    ([{"menu_item_id": 1, "quantity": 0}], 422),
    ([{"menu_item_id": 1, "quantity": "2"}], 422),
    ([], 422),
])
def test_rejected_order_writes_nothing(running, items, status):
    app, client = running
    assert client.post("/orders", json={"table": 3, "items": items}).status_code == status
    with Session(app.state.engine) as session:
        assert session.exec(select(BarOrder)).all() == []
        assert session.exec(select(OrderLine)).all() == []


def test_failure_while_inserting_lines_rolls_back_order(running):
    app, client = running
    def fail_line(_conn, _cursor, statement, parameters, _context, _many):
        if statement.startswith("INSERT INTO order_line"):
            raise IntegrityError(statement, parameters, RuntimeError("simulated storage failure"))
    event.listen(app.state.engine, "before_cursor_execute", fail_line)
    try:
        assert client.post("/orders", json=PAYLOAD).status_code == 409
    finally:
        event.remove(app.state.engine, "before_cursor_execute", fail_line)
    with Session(app.state.engine) as session:
        assert session.exec(select(BarOrder)).all() == []
        assert session.exec(select(OrderLine)).all() == []
    assert client.post("/orders", json=PAYLOAD).status_code == 201


def test_database_enforces_foreign_keys_and_quantity(running):
    app, _client = running
    with Session(app.state.engine) as session:
        session.add(OrderLine(order_id=999, menu_item_id=1, quantity=1))
        with pytest.raises(IntegrityError): session.commit()
        session.rollback()
        order = BarOrder(table_number=3)
        session.add(order); session.commit(); session.refresh(order)
        session.add(OrderLine(order_id=order.id, menu_item_id=1, quantity=0))
        with pytest.raises(IntegrityError): session.commit()
        session.rollback()


def test_multiple_lines_and_openapi(running):
    _app, client = running
    body = {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 2, "quantity": 1}]}
    response = client.post("/orders", json=body)
    assert response.status_code == 201
    assert response.json()["items"] == body["items"]
    schema = client.get("/openapi.json").json()
    assert "post" in schema["paths"]["/orders"]
    assert client.get("/docs").status_code == 200
