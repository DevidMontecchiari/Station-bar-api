"""Observable outcomes for the create-order exercise, for both variants."""
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import bar_api.api as implementation
ORDER = {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}

@pytest.fixture
def client(tmp_path):
    # Catch a misconfigured test path rather than silently checking the answer.
    variant = os.environ["BAR_CHECK_VARIANT"]
    expected = Path(__file__).resolve().parents[1] / variant / "bar_api" / "api.py"
    assert Path(implementation.__file__).resolve() == expected.resolve()
    with TestClient(implementation.create_app(tmp_path / "exercise.json")) as api:
        yield api

def test_read_menu_item(client):
    response = client.get("/menu-items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_zero_quantity_is_rejected(client):
    response = client.post("/orders", json={"table": 3, "items": [{"menu_item_id": 1, "quantity": 0}]})
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_input"

def test_create_and_retrieve_order(client):
    response = client.post("/orders", json=ORDER)
    assert response.status_code == 201, "Complete POST /orders: call the service and return the created order."
    order = response.json()
    assert order["status"] == "pending"
    assert order["table"] == 3 and order["items"] == ORDER["items"]
    assert response.headers.get("Location") == f"/orders/{order['id']}", "Set Location to the created resource URL."
    assert client.get(response.headers["Location"]).json() == order

def test_unavailable_item_is_rejected_without_saving(client):
    before = client.get("/orders").json()
    response = client.post("/orders", json={"table": 3, "items": [{"menu_item_id": 3, "quantity": 1}]})
    assert response.status_code == 422, "Delegate to the service so the availability rule is applied."
    assert response.json()["code"] == "invalid_input"
    assert client.get("/orders").json() == before
