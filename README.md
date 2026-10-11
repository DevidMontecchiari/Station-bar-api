# Station Bar API

A small backend for a bar: browse the menu, place an order for a table, and change or remove an order while it is pending. Use the example to connect an API contract, HTTP requests, validation, business rules and JSON-file storage.

## Choose your starting point

| Folder | Purpose |
| --- | --- |
| [solution](solution/README.md) | Complete menu/order CRUD example for demonstration and exploration |
| [starter](starter/README.md) | Short exercise: complete the `POST /orders` handler |
| [Demo walkthrough](docs/demo-walkthrough.md) | Requests to try and questions about the different layers |

Both versions use the same seed data and keep separate working data files. SQL or ORM experience is not required.

## Run

Use Python 3.14, matching the environment used to test this example. From this repository folder:

```sh
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Then install dependencies and start the complete example:

```sh
python -m pip install -r solution/requirements.txt
python run.py solution
```

Open **http://127.0.0.1:8000/docs** to try requests in Swagger UI. The generated contract is available at `/openapi.json`. Stop with Ctrl+C. To start the exercise instead:

```sh
python run.py starter
```

Stop one version before starting the other on the same port, or select another port with `--port 8001`. Add `--reload` when editing code.

## First request

In Swagger UI, read `GET /menu-items/1`, then call `POST /orders` with:

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
```

On fresh data the solution returns `201`, order ID `12`, status `pending` and a `Location` header. Use the returned ID for subsequent requests. The starter deliberately returns `501` for valid order creation until you complete the handler.

[Continue through the demonstration](docs/demo-walkthrough.md), or import [the Postman collection](bar-api.postman_collection.json) and set its `base_url`.

## Layers

```text
HTTP request / JSON
        |
        v
api.py + models.py   routes, input validation and HTTP responses
        |
        v
service.py           business rules and use-case logic
        |
        v
storage.py           JSON-file persistence
```

The storage layer can be replaced in a later exercise without changing the API's responsibilities. This version uses FastAPI/Python; Java/Spring or other framework implementations are not included.

## Reset the demonstration

Stop the server, then choose the relevant version:

```sh
python solution/reset_data.py --confirm
# Or: python starter/reset_data.py --confirm
```

This replaces that version's working data with `seed.json`. Seed order `11` is already ready; menu item `3` is unavailable. Working data and virtual environments are excluded from Git.

## Tests

From the repository root:

```sh
python -m pip install -r solution/requirements-test.txt
python -m pytest -q -p no:cacheprovider
```

The tests exercise the completed solution, use temporary data and check successful and failed requests against the supplied API contract. The starter's missing handler is intentional.

## Scope

This is a local teaching backend without authentication. Run one server process: JSON-file storage does not provide database transactions across multiple workers. Order status changes and production deployment are outside this example. `PUT` replaces editable fields; no `PATCH` endpoint is provided.

The original [teaching contract](solution/contracts/bar-api.published-v0.2.0.json) and the [generated contract](solution/contracts/bar-api.generated.json) are included. FastAPI produces the latter from routes and schemas; business rules still need code and tests.

References: [FastAPI request bodies](https://fastapi.tiangolo.com/tutorial/body/), [error handling](https://fastapi.tiangolo.com/tutorial/handling-errors/) and [testing](https://fastapi.tiangolo.com/tutorial/testing/).
