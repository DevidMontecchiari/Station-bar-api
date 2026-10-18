"""Optional: inspect the SAME SQLite file without an ORM or extra software."""
import os
import sqlite3
from pathlib import Path

path = Path(os.environ.get("BAR_ORM_DB", Path(__file__).parent / "data" / "bar.sqlite"))
if not path.exists():
    raise SystemExit("Start the ORM API first to initialise this database.")
# Read-only connection: this script cannot create or change the database.
with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as connection:
    connection.row_factory = sqlite3.Row
    query = """
        SELECT o.id AS order_id, o.table_number, m.name, l.quantity
        FROM bar_order AS o
        JOIN order_line AS l ON l.order_id = o.id
        JOIN menu_item AS m ON m.id = l.menu_item_id
        ORDER BY o.id, l.id
    """
    print(query)
    for row in connection.execute(query):
        print(dict(row))
