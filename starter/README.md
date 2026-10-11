# Exercise starter: create an order

Open [bar_api/api.py](bar_api/api.py). The comments guide you through three sections: supplied application setup, supplied GET handlers, and the POST handler you complete. Start with the Python refresher below and a supplied GET handler in section 2. Trace its input, function call and returned result, then edit only the marked task in section 3. The setup in section 1 is supplied and can be revisited when tracing dependency injection.

| Operation | Purpose | Your work |
| --- | --- | --- |
| `GET /menu-items/{menu_item_id}` | Inspect a drink before ordering | Supplied |
| `GET /orders` | See saved orders | Supplied |
| `GET /orders/{order_id}` | Retrieve an order by ID | Supplied |
| `POST /orders` | Create an order | Complete the marked handler |

Begin with the [guided reading warm-up](../exercises/02-create-order.md#warm-up-read-a-handler-together): trace a supplied GET handler with a partner and check one prediction in the FastAPI documentation. Then follow [exercise 2](../exercises/02-create-order.md). The input models, availability rule and JSON store are provided. `bar_api/errors.py` supplies consistent HTTP error responses; no changes to it are needed. Menu writes and order update/delete belong to the [complete reference](../solution/README.md).

## Python refresher

Read this small example before the API code. What will it print?

```python
order = {"id": 7, "table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}

def table_label(number: int) -> str:
    return f"Table {number}"

label = table_label(order["table"])
print(label)  # Table 3
```

- `order` is a variable holding a **dictionary**: named keys and values, similar to the JSON you have used. `order["table"]` retrieves `3`. `items` contains a **list** of dictionaries. A Python dictionary is an in-memory value; JSON is a text format for exchanging or storing data.
- `def` defines a **function**. Its indented lines form its body. `table_label(...)` calls it; `number` receives the argument. `return` sends the result back, and `label = ...` keeps it. `print` displays it.
- `f"Table {number}"` builds a string by inserting a value. Change the table to `5`: predict the new output. This uses Python's f-string syntax; it is different from `{order_id}` in a FastAPI route path.
- `: int` and `-> str` are **type hints**: expected input and output types. Python alone does not enforce these hints. FastAPI and Pydantic use the declared types and constraints to validate API data.

### Values, lookups and calls

Using the `order` dictionary above:

```python
table_number = order["table"]       # Dictionary lookup: 3
first_item = order["items"][0]      # First item in the list; indexes start at 0
quantity = first_item["quantity"]  # 2
is_table_three = table_number == 3 # Comparison: True
```

`=` assigns a value; `==` compares two values. Quoted text such as `"table"` is a string; `table_number` without quotes is a variable name. Python writes `True`, `False` and `None`; JSON uses `true`, `false` and `null`.

Parentheses call a function or method: `table_label(3)` runs the function. Square brackets select an item: `order["table"]` looks up a key. A dot accesses an object's attribute or method: `service.get_record(...)` calls a method on `service`.

## Reading the API code

Read the following alongside [api.py](bar_api/api.py). The [official FastAPI references](#official-fastapi-documentation) below connect each topic to its documentation. FastAPI calls a handler a *path operation function*. The snippets show supplied code or isolated expressions; the POST answer is still yours to write. The final setup subsection is a reference to return to when needed.

### 1. Trace a supplied GET handler

```python
@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: RecordId, service: Service):
    return service.get_record("orders", order_id)
```

For `GET /orders/7`, read it in this order:

1. **Choose the handler.** `@app.get(...)` is a decorator that registers the function for GET requests matching this path. `{order_id}` is the variable part of the URL; it is not an f-string. Python's function name `read_order` is not the URL.
2. **Prepare the arguments.** FastAPI reads `7` from the URL and validates it using `RecordId`. It also obtains `service` through the supplied dependency setup. The caller sends an ID, not a service object.
3. **Run the function body.** `service.get_record("orders", order_id)` asks the application service for order 7. The quotes around `"orders"` identify the collection name; `order_id` supplies the current variable's value.
4. **Return the result.** `return` hands the result back to FastAPI. `response_model=Order` describes and validates the output before it is sent as JSON. If order 7 does not exist, the supplied error handling returns `404` instead.

The parameter names after `def` name the function's inputs. A colon after each name introduces its type hint; the colon at the end of the `def` line starts the indented body. These route functions are inside `create_app`, so their bodies are indented further. Keep the existing indentation when editing.

### 2. Recognise the types and models

```python
RecordId = Annotated[int, PathParameter(ge=1)]
```

This creates a reusable type alias: an integer with extra information telling FastAPI to require a path value greater than or equal to 1. Plain `int` is a Python type; `PathParameter(...)` supplies a framework constraint. Similarly, `list[Order]` means a list whose elements match `Order`.

In [models.py](bar_api/models.py), `OrderInput` describes the request's `table` and `items`; `OrderLine` describes each item's `menu_item_id` and `quantity`. `Field(min_length=1)` requires at least one item, and `PositiveInt` requires a positive integer. `class Order(OrderInput)` inherits those fields and adds the output fields `id` and `status`.

These are Pydantic classes: FastAPI uses them to parse and validate data. For example, `quantity: 0` is rejected before the handler runs. Checking whether the menu item exists and is available belongs to [service.py](bar_api/service.py).

### 3. Understand the POST arguments

```python
@app.post("/orders", response_model=Order, status_code=201)
def create_order(body: OrderInput, response: Response, service: Service):
    # Your implementation goes here.
    ...
```

The `...` above only marks omitted code in this guide. In your file, replace the existing `raise HTTPException(...)` placeholder inside the exercise markers.

| Parameter | Where it comes from | What you use it for |
| --- | --- | --- |
| `body` | Request JSON, parsed into an `OrderInput` object | Obtain the validated order fields |
| `response` | A response object supplied by FastAPI | Set HTTP headers such as `Location` |
| `service` | The configured `BarService`, supplied through `Depends` | Apply order rules and save the new order |

`body` is a Pydantic object, so `body.table` accesses its table value. `body.model_dump()` converts it into a Python dictionary; on that dictionary, use `["table"]` instead. It does not produce a JSON string or save anything. The service expects the dictionary and returns a new order dictionary containing the assigned ID and status.

Keep a returned value with `name = function_call(...)`, as in the refresher's `label = table_label(...)`. Choose a meaningful variable name and use it consistently. For a returned order dictionary, `["id"]` retrieves its ID; an f-string can insert that value into a path. `response.headers["Location"] = ...` sets a header; it does not set the response body. Return the order data to provide the body. `print(...)` only writes to the terminal.

The route already declares successful status `201`. The current `raise HTTPException(status_code=501, ...)` deliberately stops the handler with an error until you replace it. Code after that `raise` would not run.

### 4. Revisit the supplied setup

`from .models import Order` imports a name from this package's `models.py`. `Path as PathParameter` gives an imported name a different local name, keeping it distinct from `pathlib.Path`, which represents a file path.

[main.py](main.py) calls `create_app(...)` when the application is loaded. The factory creates the app and its collaborators, registers the routes and returns the app. It is not called for every HTTP request.

```python
app.state.service = BarService(JsonStore(data_file))
```

Read the nested call from the inside out: create a `JsonStore` for the file, pass it to a new `BarService`, then store that service on the app. A class describes objects; calling its name constructs one. In `BarService`, `__init__` initialises the object and `self.store` retains its storage collaborator. `self` refers to that particular service object.

```python
def get_service(request: Request) -> BarService:
    return request.app.state.service

Service = Annotated[BarService, Depends(get_service)]
```

FastAPI supplies `request`. This provider retrieves the service created during setup. `Depends(get_service)` passes the function itself, without `()`, so FastAPI can call it and supply its return value to the handler's `service` parameter. Our provider returns this app's existing service; it does not construct a new one for each request. This behaviour comes from our setup, not from a rule that every dependency must be shared.

You can use the supplied service without recreating the factory or dependency setup in this exercise.

## Your edit and common errors

Keep the decorator and function signature. Complete the three steps in [exercise 2](../exercises/02-create-order.md) inside the existing markers, at the same indentation as the placeholder. Save before checking. You do not need to edit the models, service, storage or error handlers.

| What you see | What to check |
| --- | --- |
| `IndentationError` | Align your statements with the existing function body; use spaces consistently |
| `SyntaxError` | Inspect the reported line and the line above for missing quotes, brackets or a colon |
| `NameError` | Check variable spelling and that you assigned it before using it |
| `KeyError` | Check the dictionary key, e.g. `"id"`; request fields and returned fields differ |
| HTTP `501` for a valid POST | The placeholder is still running; check the edited file, saved changes and port 8001 |
| HTTP `422` | Read the response and check the input values or availability rule; deliberate invalid examples should fail |
| A failed check | Read the assertion message: it identifies a difference between expected and actual behaviour |

## Run and check

In your browser Codespace, run `python run.py starter --host 0.0.0.0 --port 8001 --reload` from the repository root. Open port 8001 from Ports and add `/docs`. Python changes reload automatically.

Run `python check.py starter` in a free terminal. Initially two checks pass and two fail; all four should pass after the handler is complete. The full reference suite is for `solution/`, whose API supports more operations.

After your attempt, compare only the marked `create_order` handler in [solution/bar_api/api.py](../solution/bar_api/api.py). The full reference contains additional routes for later exploration. Its supplied contract covers that wider API; the starter's `/docs` shows the smaller exercise API.

## Why are there several requirements files?

A dependency is a package our code uses. Start with [requirements.txt](requirements.txt): it lists the three main application packages.

| Package | Role in the bar app |
| --- | --- |
| `fastapi` | Connect HTTP requests to handlers and generate the API documentation |
| `pydantic` | Define and validate request/response data shapes |
| `uvicorn` | Run the application and listen for HTTP requests |

[requirements-test.txt](requirements-test.txt) includes that list using `-r requirements.txt`, then adds `pytest` (the check runner), `httpx` (the test HTTP client) and `jsonschema` (reference-contract checks).

These packages have dependencies of their own: FastAPI uses Starlette, Pydantic uses `pydantic_core`, and pytest uses supporting packages such as `pluggy`. These are **indirect dependencies** in our installation list; pip installs them automatically.

The long [requirements-lock.txt](requirements-lock.txt) records the original tested Windows environment, including those indirect packages and test tools. Its 28 entries are not 28 separate things to learn. It is an environment snapshot; our current Codespaces setup installs `requirements-test.txt`, not this snapshot.

`==` selects an exact package version. For this exercise, Codespaces prepares the packages and you can leave these files as supplied. Built-in modules such as `json` and `pathlib` come with Python and do not need entries here. More detail: [pip requirements file format](https://pip.pypa.io/en/stable/reference/requirements-file-format/) and [environment snapshots with pip freeze](https://pip.pypa.io/en/stable/cli/pip_freeze/).

## Official FastAPI documentation

Use these pages when you want another example or an explanation of a framework feature. The bar scenario and the division into API, service and storage files are our teaching example.

| In this starter | Official documentation |
| --- | --- |
| `FastAPI()`, `@app.get`, handler functions and `/docs` | [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/) |
| `{order_id}` and typed URL values | [Path Parameters](https://fastapi.tiangolo.com/tutorial/path-params/) |
| `body: OrderInput`, Pydantic input models and `model_dump()` | [Request Body](https://fastapi.tiangolo.com/tutorial/body/) |
| `response_model=Order` and output validation | [Response Model - Return Type](https://fastapi.tiangolo.com/tutorial/response-model/) |
| Setting `response.headers["Location"]` | [Response Headers](https://fastapi.tiangolo.com/advanced/response-headers/) |
| `Annotated`, `Depends` and the supplied service | [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/) |
| `raise HTTPException(...)` and error handling | [Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) |

Start with **First Steps** and **Request Body**; consult the other pages as needed. For running this particular repository, follow the commands in [Run and check](#run-and-check) above.

[Setup and learning path](../README.md) | [Code map](../docs/code-map.md)
