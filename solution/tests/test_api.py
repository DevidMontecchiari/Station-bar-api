import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from bar_api.api import create_app

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "contracts/bar-api.published-v0.2.0.json").read_text(encoding="utf-8"))
ORDER = {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
MENU = {"name": "Hot chocolate", "price": 6.0, "currency": "CHF", "available": True}

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "bar.json")) as api:
        yield api

def conforms(response, path, method):
    operation = CONTRACT["paths"][path][method]
    spec = operation["responses"][str(response.status_code)]
    if "content" in spec:
        schema = spec["content"]["application/json"]["schema"]
        Draft202012Validator({**schema, "components": CONTRACT["components"]}).validate(response.json())
    else:
        assert response.content == b""
    if "Location" in spec.get("headers", {}):
        assert response.headers["Location"].endswith(str(response.json()["id"]))

def test_order_lifecycle_and_reference_contract(client):
    menu = client.get("/menu-items/1")
    assert menu.status_code == 200
    conforms(menu, "/menu-items/{menu_item_id}", "get")
    created = client.post("/orders", json=ORDER)
    assert created.status_code == 201
    assert created.json() == {"id": 12, "status": "pending", **ORDER}
    conforms(created, "/orders", "post")
    location = created.headers["Location"]
    read = client.get(location)
    assert read.json() == created.json()
    conforms(read, "/orders/{order_id}", "get")
    replacement = {"table": 3, "items": [{"menu_item_id": 1, "quantity": 3}]}
    updated = client.put(location, json=replacement)
    assert updated.status_code == 200
    assert updated.json()["items"][0]["quantity"] == 3
    conforms(updated, "/orders/{order_id}", "put")
    listing = client.get("/orders")
    conforms(listing, "/orders", "get")
    assert len(listing.json()) == 2
    deleted = client.delete(location)
    assert deleted.status_code == 204
    conforms(deleted, "/orders/{order_id}", "delete")
    missing = client.get(location)
    assert missing.status_code == 404
    conforms(missing, "/orders/{order_id}", "get")
    assert client.post("/orders", json=ORDER).json()["id"] == 13  # deleted IDs not reused

def test_menu_crud_and_referenced_item_rule(client):
    created = client.post("/menu-items", json=MENU)
    assert created.status_code == 201
    conforms(created, "/menu-items", "post")
    location = created.headers["Location"]
    assert client.get(location).json() == created.json()
    changed = client.put(location, json={**MENU, "price": 6.5})
    assert changed.status_code == 200 and changed.json()["price"] == 6.5
    conforms(changed, "/menu-items/{menu_item_id}", "put")
    listing = client.get("/menu-items")
    conforms(listing, "/menu-items", "get")
    assert len(listing.json()) == 4
    deleted = client.delete(location)
    assert deleted.status_code == 204
    conforms(deleted, "/menu-items/{menu_item_id}", "delete")
    conflict = client.delete("/menu-items/2")  # ready order 11 refers to item 2
    assert conflict.status_code == 409
    conforms(conflict, "/menu-items/{menu_item_id}", "delete")
    item = client.get("/menu-items/2").json()
    fields = {k: v for k, v in item.items() if k != "id"}
    assert client.put("/menu-items/2", json={**fields, "available": False}).status_code == 200
    assert client.get("/orders/11").status_code == 200

@pytest.mark.parametrize("body", [
    {"table": 3, "items": [{"menu_item_id": 1, "quantity": 0}]},
    {"table": 3, "items": [{"menu_item_id": 1, "quantity": "2"}]},
    {"table": 3, "items": [{"menu_item_id": 1, "quantity": True}]},
    {"table": 3, "items": []},
    {"items": [{"menu_item_id": 1, "quantity": 2}]},
    {**ORDER, "status": "ready"},
    {**ORDER, "id": 88},
    {"table": 3, "items": [{"menu_item_id": 3, "quantity": 1}]},
    {"table": 3, "items": [{"menu_item_id": 999, "quantity": 1}]},
])
def test_invalid_order_does_not_change_data(client, body):
    before = client.app.state.service.store.path.read_bytes()
    failed = client.post("/orders", json=body)
    assert failed.status_code == 422
    conforms(failed, "/orders", "post")
    assert failed.json()["code"] == "invalid_input"
    assert client.app.state.service.store.path.read_bytes() == before

@pytest.mark.parametrize("method", ["put", "delete"])
def test_ready_order_is_protected(client, method):
    before = client.app.state.service.store.path.read_bytes()
    response = client.request(method, "/orders/11", **({"json": ORDER} if method == "put" else {}))
    assert response.status_code == 409
    conforms(response, "/orders/{order_id}", method)
    assert client.app.state.service.store.path.read_bytes() == before

@pytest.mark.parametrize("collection", ["orders", "menu-items"])
@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_missing_record(client, collection, method):
    body = ORDER if collection == "orders" else MENU
    response = client.request(method, f"/{collection}/999", **({"json": body} if method == "put" else {}))
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"

@pytest.mark.parametrize("path", ["/orders/coffee", "/orders/0", "/menu-items/-1"])
def test_invalid_path_uses_consistent_error(client, path):
    response = client.get(path)
    assert response.status_code == 422
    assert set(response.json()) == {"code", "message"}

def test_put_requires_all_editable_fields(client):
    created = client.post("/orders", json=ORDER)
    response = client.put(created.headers["Location"], json={"table": 8})
    assert response.status_code == 422
    assert client.get(created.headers["Location"]).json() == created.json()
    assert client.patch(created.headers["Location"], json={"table": 8}).status_code == 405

def test_malformed_json_has_the_contract_error_shape(client):
    response = client.post("/orders", content='{"table":', headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    conforms(response, "/orders", "post")

def test_storage_survives_a_new_application_instance(tmp_path):
    path = tmp_path / "bar.json"
    with TestClient(create_app(path)) as first:
        response = first.post("/orders", json=ORDER)
    with TestClient(create_app(path)) as second:
        assert second.get(response.headers["Location"]).json() == response.json()
        assert second.post("/orders", json=ORDER).json()["id"] == 13

def test_generated_document_describes_implemented_operations(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    generated = response.json()
    for path, methods in CONTRACT["paths"].items():
        for method, operation in methods.items():
            if method == "parameters": continue
            actual = generated["paths"][path][method]
            assert actual["operationId"] == operation["operationId"]
            assert set(operation["responses"]) <= set(actual["responses"])
            if "422" in actual["responses"]:
                assert actual["responses"]["422"]["content"]["application/json"]["schema"]["$ref"].endswith("/Error")
    assert '"HTTPValidationError"' not in json.dumps(generated)
    assert client.get("/docs").status_code == 200
