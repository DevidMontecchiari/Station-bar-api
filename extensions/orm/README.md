# Optional extension: the bar with SQLite and an ORM

[Repository overview](../../README.md) > [Exercise 4: persistence](../../exercises/04-persistence.md) > **ORM example**

**Storage: SQLite database through an ORM | API port: 8002 | Folder: `extensions/orm/`**

Looking for the JSON version? Open the [complete JSON solution](../../solution/README.md), or compare [all three versions](../../README.md#choose-the-version-json-files-or-sqlite).

The waiter still orders two coffees for table 3. The API now saves related rows in SQLite instead of rewriting a JSON file. Read the code with the lecturer before running this example. Project adoption is optional; the JSON solution remains valid.

## Classroom stages

**Enter this folder in Part D / block 3**, after the JSON demonstration, storage explanation and relational sketch. The opening demo uses `solution/`, not this folder.

1. **Read with the lecturer:** [Hero-to-bar comparison](#from-the-hero-tutorial-to-the-bar), [session](#what-is-a-session) and [one request through the code](#follow-one-request-through-the-code). Follow the selected functions shown on the slides; you do not need to read every file now.
2. **Start when the setup slide appears:** [Run in your Codespace](#run-in-your-codespace), then open 8002 `/docs`.
3. **Follow the guided requests:** [Predict, run, inspect, explain](#predict-run-inspect-explain), through the unavailable-item rejection. Stop here and keep the menu state; no query edit yet.
4. **After the third break, Part E:** [filter the menu](#class-experiment-filter-the-menu). Stop when you have predicted IDs, observed IDs and an explanation; compare with the answer only after trying.
5. **Finish with your own project:** [justify a storage choice](../../exercises/04-persistence.md#apply-the-comparison-to-your-project). DELETE, tests and further tutorials remain available for follow-up.

## What you need for this lesson

You are not expected to know or write SQL for this activity. Work programmatically with mapped Python classes, objects and ORM methods: read with `session.get()` or a Python `select()` expression; save changes with `session.add()` and `session.commit()`; remove objects with `session.delete()`.

FastAPI handles HTTP requests. SQLModel, built on SQLAlchemy, provides the object-to-table mapping and database operations. This follows the same broad ORM idea as JPA/Hibernate in Java, although the APIs differ and this example does not provide Spring Data repository interfaces. The ORM generates the SQL sent to SQLite.

You still need to understand what a record represents, how IDs link records, and which changes belong in one transaction. The class introduces those concepts. SQL text and SQL inspection are optional exploration for students who already know SQL or want to investigate further.

## Run in your Codespace

Use your own Codespace. No software installation on your laptop is required. This example uses a separate Python environment **inside the Codespace**, so the earlier exercises keep their dependencies. **The default Codespace Python is prepared for the JSON examples. The ORM packages are installed separately below.** Forwarding port8002 only makes the running API accessible; it does not install packages.

### Update an existing Codespace

Before starting, follow [Check, fetch and update your Codespace](../../docs/updating-your-codespace.md). It covers preserving your changes, syncing a fork and applying the new startup reminder. Reopening alone does not retrieve the new example. Return here for the Part D setup after updating.

### Start the ORM example in Part D

Run from the repository root (the folder containing `starter/`, `solution/` and `extensions/`).

**1. Prepare the ORM environment once:**

```sh
python -m venv extensions/orm/.venv
extensions/orm/.venv/bin/python -m pip install -r extensions/orm/requirements.txt
```

**2. Start the API with that environment's Python, every time:**

```sh
extensions/orm/.venv/bin/python extensions/orm/run.py --host 0.0.0.0
```

Use the full Python path shown above for both installation and launch; no activation command is required. Plain `python extensions/orm/run.py` uses whichever Python your terminal currently selects, which may be the JSON environment. The short command in `run.py` assumes its dependencies are already available in that interpreter.

After reopening the same Codespace, use the start command again. Repeat the installation command when the ORM requirements change. If the environment is missing or no longer works after a container/Python update, recreate it and reinstall its requirements.

### If you see `No module named sqlalchemy` or `sqlmodel`

The selected Python environment does not have the ORM packages. Complete step1, then use the exact start command in step2. Installing packages with plain `pip` or another Python can put them in a different environment.

To check which Python has the packages, stop the API with Ctrl+C and run:

```sh
extensions/orm/.venv/bin/python -c "import sys, sqlalchemy, sqlmodel; print(sys.executable)"
```

The printed path should point inside `extensions/orm/.venv`. If an import fails, rerun the installation command above. Installing ORM packages in the global Codespace Python may make a plain launch work, but the documented workflow keeps them isolated from the earlier exercises.

### Open and stop the API

In **Ports**, open **8002**, then append `/docs`. If absent, add/forward port 8002 manually. Keep it Private. Ports 8000 and 8001 belong to the earlier JSON solution and starter; 8002 lets this database variant run alongside them. This is a separate API process, not a database server port. SQLite runs within this process.

Stop with Ctrl+C. Restart using the start command from step2. The file `extensions/orm/data/bar.sqlite` stays in this Codespace; deleting the Codespace or the data file loses this demo data. It is ignored by Git. This example starts with the same three menu items and **no orders**. Use the returned order ID, not a fixed number.

Optional local Windows route, after Python is installed:

```powershell
python -m venv extensions/orm/.venv
extensions/orm/.venv/Scripts/python.exe -m pip install -r extensions/orm/requirements.txt
extensions/orm/.venv/Scripts/python.exe extensions/orm/run.py
```

Open http://127.0.0.1:8002/docs locally. For Python/terminal problems, see [local setup help](../../docs/python-setup.md).

## Classes, mapping and storage are separate choices

A UML class diagram guides your classes, fields and relationships. A normal Python class or a Pydantic request model does not automatically map to a database. In SQLModel, `table=True` and fields such as `primary_key` and `foreign_key` declare relational mapping. Engine configuration, table creation and save/query operations are separate steps. This is comparable in purpose to JPA entity mapping and a configured datasource in Java.

- **Python objects in RAM:** a list of objects is not an in-memory relational database. Without a save/load mechanism, process-local data disappears when the process ends.
- **JSON files:** the current solution explicitly loads and saves one document. One or several JSON files can be a valid project choice; with several files, explain how related updates remain consistent.
- **ORM with SQLite:** mapped classes work with a configured database. Our supplied variant uses a file, `data/bar.sqlite`. SQLite can instead be configured to keep a database in memory, but that database disappears when its owning connection lifetime ends. It still has tables and database operations. It is not the session's collection of Python objects.

Declaring classes does not automatically create an in-memory database and later turn it into a persistent one. The storage configuration is a separate choice. Changing the target does not copy existing data or remove the need to check schema, constraints and configuration. See [SQLModel table creation](https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/) and [SQLAlchemy SQLite connection options](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html).

For coaching, justify the simplest approach that supports your workflow and show that it works. JSON remains valid; ORM adoption is optional. No technology choice alone determines a project grade.

## What is a session?

A session is a Python object we use to read database records and track the objects we change. In this application, each request gets its own session. For an order, the service uses it to read the menu, check availability and track the new order and lines.

`commit()` keeps the completed writes; `rollback()` undoes uncommitted writes if saving fails. The session closes after use, while committed records remain in the database. Closing alone does not save changes. A read-only request needs no write commit.

### Trace the transaction outcome

The methods below come from SQLAlchemy's `Session`, used here through SQLModel. These are short summaries of the linked method definitions, applied to our example.

| Method | What it does here |
| --- | --- |
| [`session.add(order)`](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.add) | Registers a new mapped object with the session. Its INSERT waits for a flush. Existing persistent objects are already tracked, so changing one does not always need another `add()`. |
| [`session.flush()`](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.flush) | Writes all pending creations, modifications and deletions as database operations within the current transaction. It does **not** commit; it may run several times in one transaction. |
| [`session.commit()`](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.commit) | Flushes any remaining changes, then commits the current database transaction. |
| [`session.rollback()`](https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.Session.rollback) | Rolls back the current transaction, cancelling its uncommitted writes. Earlier successful commits remain. |

In [create_order](service.py), the first flush obtains `order.id`, which the new lines need as their `order_id`. That ID does **not** prove the transaction has committed. The service adds and flushes the lines, prepares the response, then commits the complete change. The simplified slide omits the second explicit flush and response construction; `commit()` still flushes any remaining changes.

If flushing fails, the database transaction is rolled back; the session still needs an explicit `rollback()` before it can be reused. Our error path calls it and re-raises the exception. No partial new order or lines remain. The normal unavailable-item rejection happens before the writes, so it is a different path from a failure during saving. Rollback is not a general undo of ordinary Python variables or external actions.

**Further detail:** some queries trigger autoflush. `commit()` flushes pending changes even when autoflush is disabled. The optional `objects` argument of `flush()` is for very narrow cases and is not needed here. See [SQLAlchemy: flushing and recovery after an error](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#flushing).

The slides show commit and rollback as alternative outcomes of the same unfinished transaction. After successful commit, our file-backed records survive session closure and an API restart. This persistence comes from the chosen storage, not merely from having a session.

## From the Hero tutorial to the bar

The class first walks through the [official FastAPI Hero example](https://fastapi.tiangolo.com/tutorial/sql-databases/). It starts with one table, then separates the input (`HeroCreate`), stored record (`Hero`) and public response (`HeroPublic`). A session supplies the database operations; `add`, `commit`, `refresh` and `get` connect the request to saved data. The core slides show the JSON input/output and mapped record; detailed setup and model-inheritance declarations are linked extras, alongside optional PATCH and DELETE. Memorising all the declarations is not the aim.

Use that small example to recognise the same responsibilities here. Our bar adds related order/line records and availability rules: the service checks the menu and commits an order with its lines together. We run this bar folder in class; you do not need a second Hero installation. The complete Hero tutorial is available for independent practice in a separate folder.

## Follow one request through the code

1. [main.py](main.py): `POST /orders` receives JSON as `OrderInput`. `Depends(get_session)` supplies a database session; the client does not send it. The provider yields it and closes it after the request.
2. [models.py](models.py): compare `OrderInput` with `BarOrder` and `OrderLine`. Only classes with `table=True` map to tables. `primary_key` identifies a row; `foreign_key` links to another table. An API message and a table need not have identical fields.
3. [service.py](service.py): `create_order` checks menu availability, adds an order and its lines, then commits. `flush()` sends pending SQL to the database and obtains IDs; **it does not commit**. `rollback()` undoes pending writes if storage fails. `read_order` turns related rows back into nested JSON.
4. [database.py](database.py): supplied setup creates an engine, enables SQLite foreign keys, creates missing tables and seeds a new schema. A **session** tracks objects and the transaction; it is neither a user login nor the database file. The **engine** manages access to the database.

The ordinary `menu_item_id` field stores a foreign key. We deliberately use explicit queries here; an ORM `Relationship` attribute is a separate convenience for navigating related objects, not a prerequisite for a database relationship.

## Predict, run, inspect, explain

Use Swagger UI on port8002 for the requests below. To see what is saved, keep the [database viewer](#browse-the-tables-in-vs-code) or a second terminal beside it. The viewer is optional. From the repository root, the supplied read-only fallback is:

```sh
extensions/orm/.venv/bin/python extensions/orm/inspect_data.py
```

Refresh/reopen the viewer or rerun the script after an operation. It prints joined order lines, not all tables; no result rows before you create an order is normal. The [written inspection checklist in Exercise4](../../exercises/04-persistence.md#inspect-what-was-saved) follows the same sequence.

1. **Read:** GET `/menu-items`. Which menu item is unavailable?
2. **Create:** POST `/orders` with the JSON below. Expect 201, a generated ID and a Location header.

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
```

3. **Inspect:** GET `/orders/{order_id}` using the returned ID. Match its `items` to the `BarOrder` and `OrderLine` objects in `service.py`. Identify the order ID, table number, menu-item reference and quantity. No SQL command is needed. Then inspect the saved rows: match `bar_order.id` with `order_line.order_id`, and `order_line.menu_item_id` with `menu_item.id`. For the request above, expect one new order and one line with quantity2. With the script, find the matching `order_id`, `table_number`, item name and `quantity` in its output.

4. **Restart:** stop and restart the ORM API. Predict and verify whether the order is still present. Retrieve the same ID, then refresh/reopen the viewer or rerun the script; compare the saved ID and quantity. Keep the database file unchanged.
5. **Update:** PATCH `/menu-items/1` with `{"available": false}`. Try the order again. Explain why 409 comes from a business rule rather than from a missing foreign key. In the viewer, check the changed `menu_item.available` value. Compare saved orders/lines before and after the rejected POST: no new rows should appear. This rejection happens before writes, so it is different from rolling back a failed save.
**Part D checkpoint:** pause after step 5. Explain the successful order and the rejection; keep the menu state for Part E after the break. The deletion below is optional follow-up.

6. **Optional delete:** DELETE the order you created. Expect 204; reading it now returns 404. Its order lines are deleted in the same transaction. Refresh/reopen the tables or rerun the script: that order and its lines are gone. In the viewer, confirm that the menu item remains.
7. **Explain:** which JSON response fields stayed familiar, which tables were written, and which part of the application decided whether the order was allowed?

## Class experiment: filter the menu

**Part E / block 4: start when the query activity is introduced.** Work with a partner for about 12 minutes: two minutes to find the function, then ten minutes to change and check it. In your Codespace, use Quick Open (`Ctrl+P`, or `Cmd+P` on macOS) for `extensions/orm/main.py`, then Find `def list_menu`. It is inside `create_app`. [main.py](main.py) on GitHub shows the reference; edit your own Codespace copy. Keep the route decorator and the session parameter unchanged. The supplied query returns every menu item:

```python
select(MenuItem).order_by(MenuItem.id)
```

1. Read `GET /menu-items` and note the current availability values. Predict the IDs that should remain if the query returns only available items.
2. Add a `.where(...)` condition to the Python query. Use the [SQLModel filtering guide](https://sqlmodel.tiangolo.com/tutorial/where/) if needed. `select()` and `.where()` build a query expression; they are not a SQL string.
3. **Save** `main.py`. Press **Ctrl+C** in the terminal running the ORM API, then run this command from the repository root:

   ```sh
   extensions/orm/.venv/bin/python extensions/orm/run.py --host 0.0.0.0
   ```

   This example does **not** reload automatically. Open **8002 /docs** and execute `GET /menu-items` again; compare its IDs with your prediction.
4. **Compare stored and returned data:** if using the viewer, refresh/reopen `menu_item` and compare its stored IDs with the filtered response. Unavailable rows remain stored. Without the viewer, explain this from the query expression and your before/after responses; the order-line script does not list the whole menu. Explain why order creation must still check availability.

Bring back your **predicted IDs, observed IDs and explanation**. Use your actual data: after the demo disables coffee, your result differs from the initial seed.

<details>
<summary>Worked answer: open after your attempt</summary>

```python
return session.exec(
    select(MenuItem)
    .where(MenuItem.available == True)
    .order_by(MenuItem.id)
).all()
```

| Menu state | Stored IDs | Returned IDs |
| --- | --- | --- |
| Initial seed | 1, 2, 3 | 1, 2 |
| Coffee (1) disabled in the demo | 1, 2, 3 | 2 |

Filtering changes which rows appear in the response; it does not delete records. A client could still submit an unavailable item's ID directly, so the order service must keep its availability check.

</details>

Revert the query change to restore the supplied reference, or update the test expecting all menu items if you keep the new behaviour. The unchanged reference query remains available in Git. Continue with the [project storage decision](../../exercises/04-persistence.md#apply-the-comparison-to-your-project).

## Tests

```sh
extensions/orm/.venv/bin/python -m pip install -r extensions/orm/requirements-test.txt
extensions/orm/.venv/bin/python -m pytest extensions/orm/tests -q
```

Tests use temporary databases and cover restart persistence, input validation, availability, foreign keys, CRUD and rollback after an insert failure. Your classroom data is unaffected.

## Optional: inspect SQL and database rows

This section is extra material. It is not needed to complete the class experiment. Use Swagger UI to perform operations; use a database view to observe what was saved. The API response and the stored rows are two different views of the same operation.

### Browse the tables in VS Code

An optional choice is [SQLite Viewer by qwtel](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer), extension ID `qwtel.sqlite-viewer`. Its documented free viewer works in VS Code for Web and displays tables without writing SQL. It is not currently installed by this repository's devcontainer configuration. The extension also offers paid features; this walkthrough only needs viewing.

1. In your Codespace's **Extensions** view, find that exact extension and install it there.
2. Start the ORM API using the separate environment described above. In Explorer, open `extensions/orm/data/bar.sqlite`; if necessary use **Open With...** and choose SQLite Viewer. If you set `BAR_ORM_DB`, open that database file instead.
3. Inspect the `menu_item`, `bar_order` and `order_line` tables. A fresh example has three menu items and no orders; an existing database may already contain your earlier changes.
4. Send a request in Swagger on port8002, then refresh/reopen the database view before comparing rows. The viewer caches data, so do not treat an unchanged open tab as evidence that the operation failed. Use the terminal inspection below if the view remains stale.

| Operation through Swagger | What to look for in the tables |
| --- | --- |
| Create one order containing two coffees | One new `bar_order` row and one `order_line` row with `quantity=2`; match `order_id` and `menu_item_id`. Two units do not mean two separate lines. |
| Set menu item1 to unavailable, then try ordering it | The menu row changes. The rejected order adds no order or line rows: the application checks this rule before writing. This rejection does not itself demonstrate a database rollback. |
| Optional: delete the created order | Its order row and associated lines disappear together; the menu item remains. |

Make changes through the API so its business rules run; use the viewer to observe them. No database-server port is needed: SQLite is a file used by the application. The viewer's documented web compatibility has been checked; this exact Codespace UI workflow still needs a classroom rehearsal.

### Inspect saved order lines without installing an extension

The supplied read-only inspection script runs its built-in query and prints saved order lines with their order ID, table, menu-item name and quantity. No SQL writing is needed. With no orders it prints the query but no result rows; it is not a browser for every table. Run it again after an operation to get fresh results, in another Codespace terminal:

```sh
extensions/orm/.venv/bin/python extensions/orm/inspect_data.py
```

### See the ORM operations in the terminal

To see SQL in the Codespace terminal, stop the API and restart it with:

```sh
BAR_SQL_ECHO=1 extensions/orm/.venv/bin/python extensions/orm/run.py --host 0.0.0.0
```

SQL logging is optional demonstration material, not required project configuration. This uses SQLAlchemy engine logging: it shows issued statements and transaction events, rather than a table browser. See [SQLAlchemy logging](https://docs.sqlalchemy.org/en/20/core/engines.html#configuring-logging).

For a later code walkthrough, the [VS Code Python debugger](https://code.visualstudio.com/docs/python/debugging) can stop in `service.py` to inspect objects before and after `flush()`/`commit()`. Configure it with the ORM environment interpreter. Debugger variables show application state; they are not evidence that another database connection can already read uncommitted rows. Debugger setup is not required for this lesson.

## Scope and further study

This is a small comparison application, **not a complete replacement for `solution/`**. It implements five routes and only pending orders. Successful order messages retain the earlier `table` and nested `items` shape; errors use FastAPI's standard `detail` format. It does not claim compatibility with every endpoint/error in the published bar contract. It does not import your old `data.json`.

This single-user classroom example omits authentication, production migrations and robust concurrent order/availability coordination. `create_all()` creates missing tables; it does not migrate changed columns. A transaction keeps the order and lines together, but does not automatically solve every concurrent business-rule race. Do not expose the demo publicly.

The application still has to choose useful queries, relationships and transaction boundaries. Relational modelling remains important. Deeper SQL knowledge helps with debugging and advanced queries, but SQL syntax is not a prerequisite for this lesson. SQLite is a database engine; SQLModel is an ORM library; PostgreSQL is an alternative database server. A PostgreSQL-backed generated API (for example PostgREST) is another architectural choice, not a feature that PostgreSQL itself automatically exposes over HTTP.

Official references: [FastAPI SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/), [SQLModel sessions with a dependency](https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/), [SQLModel Python queries](https://sqlmodel.tiangolo.com/tutorial/where/), [SQLModel relationship attributes](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/define-relationships-attributes/), [SQLAlchemy tutorial](https://docs.sqlalchemy.org/en/20/tutorial/), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html), [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html).

[Back to exercise 4](../../exercises/04-persistence.md) | [Earlier order exercise](../../exercises/02-create-order.md) | [Repository overview](../../README.md)
