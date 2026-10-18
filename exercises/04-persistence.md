# 4. Persistence and databases

[← Previous: validation and rules](03-validation-and-rules.md) | **4. Persistence and databases** | [Back to the learning path →](../README.md#start-here)

**Goals:** explain why saved data survives stopping the application; connect orders, lines and menu items; follow how mapped Python objects are read and saved. Watch the opening JSON demonstration, explain it together, sketch the relationships, then follow the ORM walkthrough and query experiment. SQL syntax is not required.

The [repository overview](../README.md#where-to-work-in-this-lesson) shows which folder to use at each stage. ORM is taught as a comparison; adopting it in your project remains optional.

## Classroom quick start

Open the **Station Bar API link on Moodle**, then this exercise from the repository README. Open your **own Codespace** to run or edit; a GitHub code link is for reading the reference. Earlier exercises and the JSON starter/solution remain available.

This guide accompanies the whole lesson. **Watch the opening demo, then follow each part with the lecturer.** At the end of an activity, stop where indicated and join the debrief before continuing. There is no student setup task at the start.

| Part / teaching block | Start here | Finish this part when... | Continue when introduced |
| --- | --- | --- | --- |
| A / block 1: watch and predict | [Observe JSON persistence](#part-a---observe-json-persistence); lecturer runs `solution/` on 8000 | You have predicted and observed whether the same order survives stopping/starting the application. | [B: explain JSON storage](#part-b---explain-json-storage) |
| B / block 1: guided explanation | [Supplied store](#how-the-supplied-store-works): `__init__`, `load`, `save`; `BarService.create_order` | You can explain where the data is saved and why existing data is not seeded again. | [C: related records](#part-c---sketch-related-records), after the first break |
| C / block 2: pair sketch | [Add a second line](#pair-activity-add-a-second-line), after the tables/keys explanation | You have one additional line row, the two-line response JSON and an explanation of reused IDs. | [D: ORM walkthrough](#part-d---follow-the-orm-comparison), after the second break |
| D / block 3: read code, then run | [ORM guide](../extensions/orm/README.md#classroom-stages): mapped classes/session, then setup on 8002 and guided requests | You have seen a saved order retrieved and an unavailable item rejected; no query edit yet. | [E: query experiment](#part-e---change-one-query), after the third break |
| E / block 4: your bounded change | [Filter the menu](../extensions/orm/README.md#class-experiment-filter-the-menu) | You have predicted IDs, observed IDs and can explain why rows remain stored. | [Project choice](#apply-the-comparison-to-your-project); further tutorials are optional |

**Find a function in VS Code:** Quick Open (`Ctrl+P`, or `Cmd+P` on macOS), enter the file path, then use Find for `def load`, `def save`, `def create_order` or `def list_menu`. Read the selected function with its parameters and return value; the surrounding setup is already supplied. Run commands from the repository root. JSON solution: **8000**; ORM: **8002**. Keep ports Private.

## Part A - Observe JSON persistence

**Mode: lecturer demonstration before theory.** Predict the outcome before the lecturer stops the application. Follow only the create/stop/start/retrieve sequence below.

## Try persistence

The lecturer runs the supplied solution. Students watch and predict; these commands also let you repeat the demonstration later in your own Codespace:

```sh
cd /workspaces/Station-bar-api
python run.py solution --host 0.0.0.0
```

If your repository folder has a different name, use that name in the first command. Open port 8000 and `/docs`. This path is for Codespaces; local setup is covered in the repository README.

1. In Swagger UI, expand **POST /orders**, choose **Try it out**, replace the body with the JSON below and choose **Execute**. Keep the returned ID.

   ```json
   {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
   ```
2. Press Ctrl+C, then run the same Python command again. Keep `solution/data.json`; do not reset or delete it.
3. Retrieve the same order.
**Check:** the order survives restart. In Codespaces each version uses its own data.json beside main.py; tests use temporary data.

**Transfer:** which information must survive a restart in your own application? Which operations read it or change it?

**Part A checkpoint - pause here:** record your prediction and the observed result. Keep the saved order. We now explain what happened in [Part B](#part-b---explain-json-storage); do not open the ORM setup yet.

[Codespaces stop/reset instructions](../docs/codespaces.md)

## Part B - Explain JSON storage

**Mode: guided theory and code reading.** Use the observed order as evidence. Compare memory and storage options, then follow the seed/load/change/save explanation in the slides.

Open the [storage decision guide](../docs/storage-choice.md) to follow the same diagram as in the slides. Consider one operation at a time; we return to this guide when choosing storage for your project.

## How the supplied store works

The slides **First start and later starts: the working JSON file**, **Load**, **Change** and **Save** follow one order through these behaviours:

| Behaviour | What happens in `JsonStore` |
| --- | --- |
| **Initial seed** | Seed data is the supplied sample menu and orders in `seed.json`. During setup, `__init__` uses it to create the working `data.json` only if that file is missing. Existing saved data is kept. |
| **Load** | `load()` reads the working JSON file and parses it into a Python dictionary that the service can inspect or change. |
| **Save** | `save(data)` turns the updated dictionary into JSON text, writes a temporary file and replaces the working file. |

A read operation loads data. A write operation loads data, applies its checks and changes, then saves it. Stopping and starting the application keeps the working file; an explicit reset replaces its contents with seed data.

1. Read [JsonStore](../solution/bar_api/storage.py). Match the three rows above to `__init__`, `load()` and `save(data)`. Find the condition that prevents existing data from being replaced by seed data.
2. Follow `create_order` in [the solution's BarService](../solution/bar_api/service.py): load the current data, check the requested items, add the order, then save.
3. Explain what would happen if all orders lived only in a Python list created at startup.

**Part B checkpoint - pause here:** explain why the order survived and why the seed did not overwrite it. No code edit is required. After the first break we introduce related tables, then start [Part C](#part-c---sketch-related-records).

## Part C - Sketch related records

**Mode: theory, then a pair sketch.** First follow the record/table/key examples; start the pair task when the lecturer displays it. Use paper or notes; no database setup yet.

## From the bar records to related tables

Use the same request as before: the waiter orders two coffees for table 3. The existing JSON stores an order with an `items` list. In a relational design, each order line can instead be a row linked to its order and menu item. A **primary key** identifies a row; a **foreign key** refers to a row in another table.

These illustrative rows show one new order; order 12 is an example ID, not a promise about the next ID in your working data.

| Table | Example row | Meaning |
| --- | --- | --- |
| `menu_item` | `id=1`, `name="Espresso macchiato"`, `price=4.50`, `currency="CHF"`, `available=true` | The menu item supplied in our seed data. |
| `bar_order` | `id=12`, `table_number=3`, `status="pending"` | One order; `table_number` corresponds to `table` in the existing API. |
| `order_line` | `id=1`, `order_id=12`, `menu_item_id=1`, `quantity=2` | A line linked to both the order and the menu item. The row ID is introduced for this relational example. |

One order can contain several lines. The same menu item can appear on lines in different orders. JSON remains useful at the HTTP boundary even if the application stores rows in a database; API response shapes and database tables need not be identical.

**Explain the mapping:** identify the primary and foreign keys, then sketch how you would reconstruct the API's `items` list from the rows. Where should the application reject an unavailable menu item? That business rule still belongs to the application, regardless of storage choice.

### Pair activity: add a second line

For the **sketch**, order 12 at table 3 already contains two coffees (`menu_item_id=1`). Add one cappuccino (`menu_item_id=2`).

1. Draw the new `order_line` row. Give it its own ID and identify the order and menu-item references.
2. Sketch the response's `items` list containing both lines. Explain why the quantity belongs to the line rather than the menu item.
3. State which existing rows you reuse. No new order or menu-item row is needed for this sketch.
4. Explain the difference between referencing a missing menu item and ordering an existing but unavailable item.
5. If saving a new order's second line fails, what should happen to its first line and order row? Describe the all-or-none outcome of a transaction.

**Part C checkpoint - pause here:** for the pair task, complete steps 1-3 and keep your sketch for the debrief. Steps 4-5 lead into the following discussion of constraints and transactions. Wait until block 3 to start [Part D](#part-d---follow-the-orm-comparison).

This is a modelling activity, not an instruction to implement an add-line endpoint. The runnable demo creates a new order with its lines together; use its returned ID.

## Part D - Follow the ORM comparison

**Mode: guided code walkthrough, then setup and requests.** Begin after the second break; the slides introduce ORM, the session and the Hero example before the bar setup.

Follow our [runnable bar ORM guide](../extensions/orm/README.md). Read the code with the lecturer before setup: HTTP input, mapped classes, session, checks, writes and commit. Then create/read an order, verify persistence and explain a rejected order.

Use Python classes and ORM methods. The ORM generates SQL; writing SQL statements or inspecting generated SQL is further exploration.

### Inspect what was saved

Keep these instructions open beside the [guided requests](../extensions/orm/README.md#predict-run-inspect-explain). Use **Swagger on port8002** to change data, then inspect the saved result. You do not need to write SQL.

1. **Choose a view:** follow [Browse the tables in VS Code](../extensions/orm/README.md#browse-the-tables-in-vs-code) to open `extensions/orm/data/bar.sqlite`, or use the supplied read-only script in a second terminal from the repository root:

   ```sh
   extensions/orm/.venv/bin/python extensions/orm/inspect_data.py
   ```

   The viewer shows all three tables. The script prints saved order lines with their order ID, table, item name and quantity; it does not show every table or the availability field. It requires no extra extension. Before any orders exist, it prints its query but no result rows.
2. **After creating the order:** refresh/reopen the viewer, or rerun the script. Find the returned order ID. In the viewer, match `bar_order.id` to `order_line.order_id`, then `order_line.menu_item_id` to `menu_item.id`. Two coffees in this request produce one line with `quantity=2`.
3. **After restarting the API:** retrieve the same order in Swagger and inspect the saved data again. Keep the database file; do not reset it. The ID and quantity should still match.
4. **After making coffee unavailable:** inspect `menu_item.available` in the viewer, if using it. Attempt the order again and compare the saved order lines before and after the rejection. No new order or line should appear. The service rejects this request before writing; this is not the failed-write rollback demonstration.
5. **Explain one observation:** connect a response field to its stored row, and explain one change that did or did not occur. Use your current data and returned IDs, rather than assuming the example starts empty.

The viewer is optional and may cache data: refresh/reopen after requests. If it is unavailable, use the script for the order checks. Make changes through the API and use inspection to observe them. The [inspection guide](../extensions/orm/README.md#optional-inspect-sql-and-database-rows) also covers optional SQL logging and deletion checks.


**Part D checkpoint - pause here:** complete the guided success/read/restart/rejection checks on port 8002. Keep the current menu state for the next activity. Do not change `list_menu` yet; optional DELETE is available for later exploration. After the third break, begin Part E.

## Part E - Change one query

**Mode: pairs, after the third break.** Open `extensions/orm/main.py`, find `list_menu` inside `create_app`, and change only its query expression.

For the final pair activity, [filter the menu](../extensions/orm/README.md#class-experiment-filter-the-menu): predict the returned IDs from your current data, change the query in `extensions/orm/main.py`, restart and compare. Explain why a filtered-out row is still stored. The guide includes a collapsible worked answer.

**Inspect the difference, if using the viewer:** refresh/reopen `menu_item` after the filtered GET. Compare its stored IDs with the IDs in the API response. An unavailable item can remain in the table while disappearing from the response. Do not delete rows to obtain the filtered result. The order-line script above does not list all menu items; this particular visual check uses the table viewer. Without it, explain the distinction from the read-only query expression and your before/after responses.

**Part E checkpoint - pause here:** bring back predicted IDs, observed IDs and an explanation of why a hidden row still exists. Open the worked answer after your attempt. Then use the short project discussion below; the further-reading sections are optional.

## Apply the comparison to your project

Choose one real operation in your project and discuss:

- **Requirement:** which data must survive stopping the application, and which changes must stay consistent?
- **Choice:** how does your chosen storage approach meet that requirement?
- **Evidence:** what request, restart or failure check would demonstrate that it works?

Use this sentence if helpful: **For [operation], we choose [storage] because [...]. We will check [...].** Share it briefly or add a note to your existing README. This is not a new assessed deliverable.

A working JSON-based project remains valid. ORM adoption is optional and can demonstrate initiative through a justified choice, working behaviour and explanation; it creates no automatic bonus or new requirement.

## Further exploration

To build a separate example from scratch, follow the [official FastAPI SQL database tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/), using SQLite and SQLModel. Keep that experiment in a separate folder. Identify its connection setup, mapped model, session, save/query operations and commit; try retrieving a record after stopping and starting it. The supplied bar example already includes order lines, so rebuilding them is not another classroom task.

The slides also compare other storage families and a generated API approach. These are optional choices to recognise, not systems to install. [PostgREST table/view routes](https://docs.postgrest.org/en/stable/references/api/tables_views.html) illustrate supplied CRUD; [database functions](https://docs.postgrest.org/en/stable/references/api/functions.html) provide a place for a custom order operation. The Java comparison connects to the Internet Technology class: [Spring Data JPA guide](https://spring.io/guides/gs/accessing-data-jpa/). Neither is a runnable variant in this repository.

## FastAPI reading for the next steps

Use these chapters when you reach the corresponding project question. They are optional references, not additional milestone deliverables.

| Project question | Official guide | What to look for |
| --- | --- | --- |
| How can we organise a growing set of routes? | [Bigger applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) | `APIRouter` groups related routes; `include_router` combines them into one application. Moving routes into files does not create separate services. |
| How do we check a successful and a rejected request? | [Testing](https://fastapi.tiangolo.com/tutorial/testing/), [response models](https://fastapi.tiangolo.com/tutorial/response-model/), [errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) | Assert response status and JSON. Keep the expected contract visible while changing implementation. |
| How will a frontend call this API? | [CORS](https://fastapi.tiangolo.com/tutorial/cors/), [templates](https://fastapi.tiangolo.com/advanced/templates/) | Recognise browser origins and the optional server-rendered approach. CORS is not user authentication. |
| How do we identify users and restrict operations? | [Security](https://fastapi.tiangolo.com/tutorial/security/), [permissions/scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/) | Distinguish identifying a user from deciding which operations they may perform. |
| How will setup change for deployment? | [Settings](https://fastapi.tiangolo.com/advanced/settings/), [lifespan](https://fastapi.tiangolo.com/advanced/events/), [deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/) | Separate configuration, startup/shutdown resources and deployment responsibilities. Application lifespan is different from a database session for one request. |

The supplied ORM example already separates models, service and database setup, and includes tests. Its routes are still together in `main.py`; the `APIRouter` organisation illustrated in the slides is a possible refactor, not another provided folder to run. Preserve the existing routes and responses if you experiment with it. [Dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/) are a further testing technique; the current bar tests use an application factory and a temporary database instead.

For backend coaching, prepare one working request-to-storage workflow with a success and an error case. Keep startup and demonstration steps in your existing README, check repository access and follow Moodle for the submission deadline and your Teams slot. A complete backend is not required at this milestone. JSON storage remains valid; ORM adoption is optional.

## Further setup and study references

- [FastAPI SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/): a small runnable API with SQLite and SQLModel, including table models and a session dependency.
- [SQLAlchemy Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/): deeper explanation of connections, transactions, queries and ORM mapping.
- [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html): relational concepts and SQL for a later database-server option. It is an alternative setup to explore, not a prerequisite for the earlier exercises.

For the class discussion, compare the JSON implementation with the database example: what stays the same for the API client, what changes in storage, and which new setup and consistency responsibilities appear?



---

[← Previous: validation and rules](03-validation-and-rules.md) | **4. Persistence and databases** | [Back to the learning path →](../README.md#start-here)
