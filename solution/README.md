# Complete bar API

Start from the repository root with `python run.py solution`; see the [setup instructions](../README.md#run).

Explore `main.py`, then `bar_api/api.py`, `models.py`, `service.py` and `storage.py`. The HTTP layer delegates business decisions to the service, which uses JSON-file storage. See the [walkthrough](../docs/demo-walkthrough.md) for requests to demonstrate.

Menu items and orders support create, read, replace and delete. Only pending orders can be changed or deleted. A menu item referenced by an order cannot be deleted. ID and status are assigned by the server. Error bodies contain `code` and `message`.

`requirements.txt` pins the runtime dependencies. `requirements-test.txt` adds test dependencies; `requirements-lock.txt` records the complete tested Windows/Python environment and is retained for reference.
