# 4. Follow the saved data

[← Previous: validation and rules](03-validation-and-rules.md) | **4. Persistence (next class)** | [Back to the learning path →](../README.md#start-here)

**Goal:** distinguish application state from the process that serves requests. Use the solution or your completed starter. This activity inspects the supplied storage code; SQL is not required.

## How the supplied store works

The slide **JSON storage: initialise, load and save** explains these three behaviours:

| Behaviour | What happens in `JsonStore` |
| --- | --- |
| **Initial seed** | Seed data is the supplied sample menu and orders in `seed.json`. During setup, `__init__` uses it to create the working `data.json` only if that file is missing. Existing saved data is kept. |
| **Load** | `load()` reads the working JSON file and parses it into a Python dictionary that the service can inspect or change. |
| **Save** | `save(data)` turns the updated dictionary into JSON text, writes a temporary file and replaces the working file. |

A read operation loads data. A write operation loads data, applies its checks and changes, then saves it. Restarting the API keeps the working file; an explicit reset replaces its contents with seed data.

## Try persistence

1. Create an order and keep its returned ID.
2. Stop and restart that API without resetting its data.
3. Retrieve the same order.
4. Read [JsonStore](../solution/bar_api/storage.py). Match the three rows above to `__init__`, `load()` and `save(data)`. Find the condition that prevents existing data from being replaced by seed data.
5. Follow `create_order` in [the starter's BarService](../starter/bar_api/service.py): load the current data, check the requested items, add the order, then save.
6. Explain what would happen if all orders lived only in a Python list created at startup.

**Check:** the order survives restart. In Codespaces each version uses its own data.json beside main.py; tests use temporary data.

**Transfer:** which information must survive a restart in your own application? Which operations read it or change it?

A later optional database implementation can preserve the HTTP contract while changing data access. The current store reads/writes a whole snapshot; an ORM replacement requires deliberate mapping and transaction design.

[Codespaces stop/reset instructions](../docs/codespaces.md)

---

[← Previous: validation and rules](03-validation-and-rules.md) | **4. Persistence (next class)** | [Back to the learning path →](../README.md#start-here)
