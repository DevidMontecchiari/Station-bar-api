# 2. Complete the order endpoint

[← Previous: code map](../docs/code-map.md) | [Learning path](../README.md#start-here) | [Next: validation and rules →](03-validation-and-rules.md)

**Goal:** connect an HTTP request to the supplied application logic. Work individually or in pairs. The input models, order-creation service, JSON store and three GET handlers are provided; complete only the marked POST handler.

**Before starting:** create your own Codespace from the class repository (or your fork) and wait for setup to finish. Follow [Codespaces setup](../docs/codespaces.md); no local installation is needed for this class. Local execution is an optional later route, documented in [local Python setup](../docs/python-setup.md). Run every command below from the **repository root**, where `run.py` and `check.py` are located. Keep this guide beside your editor.

## Warm-up: read a handler together

Open [starter/bar_api/api.py](../starter/bar_api/api.py). Follow the supplied `read_menu_item` handler with the lecturer, then look at `read_order` with a partner. No code changes are needed yet.

For `GET /orders/7`, assuming order 7 exists:

1. Identify the value of `order_id`, its Python type and where `service` comes from.
2. Point to the method call that retrieves the order. Explain what `return` does here and how it differs from `print`.
3. Predict what happens if the URL ends in `/orders/abc`. Use the official [Path Parameters documentation](https://fastapi.tiangolo.com/tutorial/path-params/) to check your explanation of type validation.

Compare your reasoning in class, then continue with the POST task. The [code-reading guide](../starter/README.md#reading-the-api-code) is available if you get stuck.

## 1. See what is missing

In a free terminal (**Terminal > New Terminal** if an API is already running), run:

```sh
python check.py starter
```

The output must say **Checking starter**. Initially, **2 checks pass and 2 fail**: reading and input validation work, but the order-creation handler is unfinished. A valid POST currently returns `501`. These failures are expected; the tests run without starting the API and use temporary data.

## 2. Complete the handler

Open [starter/bar_api/api.py](../starter/bar_api/api.py) in the editor. If Python feels unfamiliar, read the [short refresher](../starter/README.md#python-refresher) first. Start with a supplied GET handler in section 2: identify the input, method call and returned result. Use the [step-by-step code reading](../starter/README.md#reading-the-api-code) if you need more explanation of the syntax or parameter sources. Section 1 supplies the application and dependency setup; you can refer back to it. Section 3 introduces the POST arguments and the `BEGIN CREATE ORDER EXERCISE` task. Error-formatting support is supplied separately in `errors.py`.

Replace the placeholder inside the marked function:

- Pass the validated input to `service.create_order(body.model_dump())` and keep the returned order.
- Set the response's `Location` header to `/orders/` followed by that order's ID.
- Return the created order. The route already declares status `201`.

Save the file. Leave the surrounding routes, models, service and storage in place. You are connecting those supplied parts.

## 3. Check your change

Run the same command again:

```sh
python check.py starter
```

Expect **4 passed**. If a check fails, read its assertion message and compare it with the three responsibilities above. Confirm that you edited `starter/bar_api/api.py`, not the solution.

## 4. Try your API in the browser

From the repository root, start the starter in a **separate terminal**:

```sh
python run.py starter --host 0.0.0.0 --port 8001 --reload
```

Leave this terminal running. In Codespaces, use **Ports** to open **8001** in the browser, then add **/docs** to your forwarded address. Keep the port private. For a local run, open **http://127.0.0.1:8001/docs**. The reference, if still running, is on **8000**; test your changes on **8001**.

In Swagger UI, expand **POST /orders**, choose **Try it out**, replace the request body with the following JSON, then choose **Execute**:

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
```

| Try | Expected result | What it shows |
| --- | --- | --- |
| Send the request above | `201`, a pending order and a `Location` header | The handler calls the service and returns the saved order |
| Copy its ID into **GET /orders/{order_id}** and execute | `200`, the same order | The new order can be retrieved |
| Change `quantity` to `0` and send again | `422` | Input validation rejects a non-positive quantity |
| Use `menu_item_id: 3` with `quantity: 1` | `422` on the supplied data | The service rejects an unavailable item |

Use the returned ID rather than assuming a fixed number. Python changes reload automatically after saving. Stop an API with **Ctrl+C** in its terminal.

## Finish

You are ready to discuss your result when the four checks pass and you can show a successful creation and a rejected request. Explain which part checks the input, which applies the availability rule, and which saves the order.

After your attempt, compare the marked handler in [solution/bar_api/api.py](../solution/bar_api/api.py). The complete reference also has menu writes and order update/delete; those operations are outside this starter. To check the full reference, use `python check.py solution --full`. Checks do not change your saved demonstration orders.

**Transfer:** identify the route, service decision and saved data for one operation in your own project. No separate submission is required for this practice exercise.

---

[← Previous: code map](../docs/code-map.md) | [Learning path](../README.md#start-here) | [Next: validation and rules →](03-validation-and-rules.md)
