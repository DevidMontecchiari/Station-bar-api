"""Application rules. This module has no HTTP or FastAPI dependencies."""
from .storage import JsonStore

class BarError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

class BarService:
    def __init__(self, store: JsonStore):
        self.store = store

    @staticmethod
    def find(rows: list[dict], record_id: int) -> dict:
        for row in rows:
            if row["id"] == record_id:
                return row
        raise BarError("not_found", "Requested resource not found.")

    @staticmethod
    def check_order_items(data: dict, items: list[dict]) -> None:
        menu = {item["id"]: item for item in data["menu_items"]}
        for line in items:
            item = menu.get(line["menu_item_id"])
            if item is None or not item["available"]:
                raise BarError("invalid_input", "Each ordered item must exist and be available.")

    @staticmethod
    def check_pending(order: dict) -> None:
        if order["status"] != "pending":
            raise BarError("conflict", "Only pending orders can be changed or deleted.")

    def list_records(self, collection: str) -> list[dict]:
        with self.store.lock:
            return self.store.load()[collection]

    def get_record(self, collection: str, record_id: int) -> dict:
        return self.find(self.list_records(collection), record_id)

    def create_menu_item(self, fields: dict) -> dict:
        with self.store.lock:
            data = self.store.load()
            item = {"id": data["next_menu_item_id"], **fields}
            data["next_menu_item_id"] += 1
            data["menu_items"].append(item)
            self.store.save(data)
            return item

    def replace_menu_item(self, record_id: int, fields: dict) -> dict:
        with self.store.lock:
            data = self.store.load()
            item = self.find(data["menu_items"], record_id)
            item.update(fields)
            self.store.save(data)
            return item

    def delete_menu_item(self, record_id: int) -> None:
        with self.store.lock:
            data = self.store.load()
            item = self.find(data["menu_items"], record_id)
            if any(line["menu_item_id"] == record_id
                   for order in data["orders"] for line in order["items"]):
                raise BarError("conflict", "An order references this item; set available=false instead.")
            data["menu_items"].remove(item)
            self.store.save(data)

    def create_order(self, fields: dict) -> dict:
        with self.store.lock:
            data = self.store.load()
            self.check_order_items(data, fields["items"])
            order = {"id": data["next_order_id"], **fields, "status": "pending"}
            data["next_order_id"] += 1
            data["orders"].append(order)
            self.store.save(data)
            return order

    def replace_order(self, record_id: int, fields: dict) -> dict:
        with self.store.lock:
            data = self.store.load()
            order = self.find(data["orders"], record_id)
            self.check_pending(order)
            self.check_order_items(data, fields["items"])
            order.update(fields)
            self.store.save(data)
            return order

    def delete_order(self, record_id: int) -> None:
        with self.store.lock:
            data = self.store.load()
            order = self.find(data["orders"], record_id)
            self.check_pending(order)
            data["orders"].remove(order)
            self.store.save(data)
