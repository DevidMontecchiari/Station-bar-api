# Station Bar API

A waiter records an order for two coffees at table 3. The bar needs to remember the order and prevent changes once it is ready. Follow that one scenario from an HTTP request through validation, business rules and storage.

The backend uses [FastAPI](https://fastapi.tiangolo.com/tutorial/first-steps/). For the framework features used in the exercise, see the [official documentation links beside the starter walkthrough](starter/README.md#official-fastapi-documentation).

This repository is a running teaching reference used across several classes. The numbered exercises follow the same bar example from its API contract to implementation, validation and persistence. No SQL or ORM knowledge is required.

## Start here

**Follow the learning path:** [1. Contract](exercises/01-api-contract.md) → [Code map](docs/code-map.md) → [2. Endpoint](exercises/02-create-order.md) → [3. Validation and rules](exercises/03-validation-and-rules.md) → [4. Persistence (next class)](exercises/04-persistence.md).

Use the **Previous / Next** links at the top and bottom of each guide to move between steps. **Learning path** brings you back here.

| Exercise | What you practise |
| --- | --- |
| [1 — Read the API contract](exercises/01-api-contract.md) | Identify the operation, required input, successful response and possible errors. |
| [2 — Implement an order endpoint](exercises/02-create-order.md) | Complete `POST /orders` in the starter and check its behaviour. |
| [3 — Validation and business rules](exercises/03-validation-and-rules.md) | Try successful and rejected requests; explain which layer decides. |
| [4 — JSON persistence](exercises/04-persistence.md) | In the next class, inspect the saved data and check what survives an API restart. |

**Current classroom task: [Exercise 2 — Implement an order endpoint](exercises/02-create-order.md).** Before editing, trace the supplied code using the [code map](docs/code-map.md), then [run the complete reference](#open-in-github-codespaces) and send an order. The exercise identifies the file to edit, the checks to run and the expected responses.

`solution/` contains the **complete, runnable backend for the current class**: menu and order operations, validation, business rules and JSON storage. `starter/` is a **small order-creation exercise**, with three supplied read operations and one POST handler left to complete. Menu editing and order update/delete remain in the complete reference. **Edit `starter/` for your attempt.**

## From exercises to the complete application

We will use this repository throughout the bar exercises, extending the same application in later persistence and frontend-integration classes. The exercise guides and starter will remain available for practice and revision.

At the end of the sequence, a **clean reference download of the finished application** is planned. It will contain the complete application, setup instructions and tests, without the unfinished starter or exercise guides. It will come from the same maintained implementation in this repository.

That final download is not available yet. The current `solution/` is the completed backend for this stage; the integrated frontend and later course additions are still to come.

## Open in GitHub Codespaces

**No local installation is required for this class.** You only need a browser and your GitHub account with Codespaces access. Each student (or pair) works in their own Codespace, which provides VS Code, Python and the project dependencies in the browser. You do not need to install Python, VS Code or Docker on your computer.

Use the repository link shared for class, not the lecturer's Codespace or forwarded-port URL. GitHub clones the project into your new Codespace automatically: a local clone is not required. If you want your own repository for saving changes, fork the shared repository first and create the Codespace from your fork.

1. Sign in to your own GitHub account and open the repository shared for this class (or your fork).
2. Choose **Code > Codespaces**, then create **your own Codespace** or resume one you previously created. Wait for environment creation and dependency installation to finish.
3. In the Codespace terminal, from the repository root, run:

```sh
python run.py solution --host 0.0.0.0
```

4. In **Ports**, open port **8000** in your browser and add **/docs** to the forwarded address. Keep port visibility **Private**.

This opens the complete **solution**. Use the forwarded address from Codespaces; localhost on your laptop is a different location. [Codespaces guide](docs/codespaces.md).

In Swagger UI, open **GET /menu-items/{menu_item_id}**, select **Try it out**, enter `1`, and execute. Then open **POST /orders** and send:

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
```

Expect `201`, a pending order and a `Location` header. Follow the returned ID with **GET /orders/{order_id}**. Use the ID in your response; it changes as orders are added.

Stop an API with Ctrl+C. Each version saves its own data.json in the codespace. See [Codespaces controls and reset](docs/codespaces.md).

## Work on the starter

Open [exercise 2](exercises/02-create-order.md) beside your editor and follow its steps. If it has been a while since you used Python, start with the [short Python refresher](starter/README.md#python-refresher). Run all commands from the repository root, where `run.py` and `check.py` are located.

The starter's `bar_api/api.py` contains only the setup, three short GET handlers and the marked POST handler. The supplied `errors.py` keeps error formatting outside this exercise file. Open `models.py`, `service.py` and `storage.py` when tracing those responsibilities; no changes to them are required for this task.

**Why two ports?** We run two versions of the backend side by side in the same Codespace:

- **8000 - complete reference (`solution/`):** inspect the expected behaviour.
- **8001 - your exercise (`starter/`):** try the code you are changing.

The port determines which running API receives your request. Starting both with these commands on port 8000 would cause an "address already in use" error. Separate ports let you keep both `/docs` pages open and compare results. You could reuse one port by stopping one API before starting the other; two ports simply make comparison easier.

Start the starter from a **new terminal** (**Terminal > New Terminal**); leave the reference API running in its own terminal:

```sh
python run.py starter --host 0.0.0.0 --port 8001 --reload
```

Open port **8001** from **Ports**, then add **/docs**. Edit [starter/bar_api/api.py](starter/bar_api/api.py) in your editor; Python changes reload automatically. The solution on port 8000 remains available for comparison and has separate data.

Valid order creation initially returns **501**: that is the function you complete. The three GET handlers and validation are provided. Follow [exercise 2](exercises/02-create-order.md).

Use another free terminal to run checks against **your starter**. The checks do not need a running API:

```sh
python check.py starter
```

Initially two checks pass and two fail. After implementing the handler, all four should pass. Checks use temporary data, not your saved demonstration orders.

Save your changes, then stop the codespace when you finish. Closing its browser tab does not stop the compute session.

## Later: local execution and external clients

In the design and deployment classes, we will revisit how to run and connect to the same application:

- **Run it locally:** clone or download the repository and follow [local Python setup](docs/python-setup.md). This is an alternative for later, not preparation required for this exercise.
- **Connect Postman or a frontend:** use the local API address or a forwarded Codespaces URL. We will demonstrate changing port visibility to **Public** for external access; see [later connection options](docs/codespaces.md#later-postman-and-frontend-connections). A public port is accessible to anyone with its URL. Keep your ports **Private** for the current exercise.
- **Explore containers:** [container setup](docs/containers.md) is optional material for later. Docker installation is not part of this class.

## What is supplied

- [solution/](solution/README.md): complete menu/order CRUD, business rules, JSON storage and reference tests.
- [starter/](starter/README.md): focused create/read exercise; complete the marked order-creation handler.
- [Code map](docs/code-map.md): responsibilities and the Spring comparison.
- [Demonstration walkthrough](docs/demo-walkthrough.md): a longer sequence of requests.
- [Postman collection](bar-api.postman_collection.json): supplied for later calls to the local API or a forwarded Codespaces URL. For this exercise, use the signed-in browser and `/docs`; see [later connection options](docs/codespaces.md#later-postman-and-frontend-connections).
- [Teaching contract](solution/contracts/bar-api.published-v0.2.0.json) and [generated contract](solution/contracts/bar-api.generated.json). The live contract is at `/openapi.json`.

The reference currently covers HTTP, application logic and JSON persistence. Frontend integration, authentication and Java/Spring alternatives are later stages.

The dependency files separate the three main application packages from test tools and the recorded environment snapshot. See [why there are several requirements files](starter/README.md#why-are-there-several-requirements-files). Codespaces prepares these packages; no dependency editing is needed for the exercise.

## Scope and checks

For the current exercise, use this unauthenticated example in your private development environment, with one server process per data file. In the complete reference, `PUT` replaces editable fields; status transitions and `PATCH` are not included.

`python check.py starter` runs the four focused exercise checks. `python check.py solution --full` runs the full reference CRUD suite; those extra operations are outside the starter. The older plain `pytest` command at the repository root checks only the supplied solution.

The Codespaces configuration is prepared; hosted build/startup and private forwarded-port access still need rehearsal before classroom delivery. The Python backend and exercise checks have a separate local verification record.

Sources: [Creating your own Codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository), [GitHub Codespaces quickstart](https://docs.github.com/en/codespaces/quickstart) and [forwarded ports](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).
