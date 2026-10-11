"""Application rules. This module has no HTTP or FastAPI dependencies."""
from .storage import JsonStore

class BarError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

class BarService:
    # __init__ initialises each new BarService; self means this particular object.
    def __init__(self, store: JsonStore):
        self.store = store

    @staticmethod
    def find(rows: list[dict], record_id: int) -> dict:
        # for visits each dictionary in the list; == compares, whereas = assigns.
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

    def list_records(self, collection: str) -> list[dict]:
        with self.store.lock:
            return self.store.load()[collection]

    def get_record(self, collection: str, record_id: int) -> dict:
        return self.find(self.list_records(collection), record_id)

    def create_order(self, fields: dict) -> dict:
        with self.store.lock:
            data = self.store.load()
            self.check_order_items(data, fields["items"])
            # **fields copies the input dictionary entries into this new dictionary.
            order = {"id": data["next_order_id"], **fields, "status": "pending"}
            data["next_order_id"] += 1  # Increase the next ID by one.
            data["orders"].append(order)  # Add the new dictionary to the orders list.
            self.store.save(data)
            return order

