# Start the frontend class examples

[Repository overview](../README.md) · [Frontend walkthrough](../extensions/frontend/README.md)

After [safely updating your Codespace](updating-your-codespace.md), open a terminal at the repository root and run:

```sh
python start_class.py
```

Or choose **Terminal → Run Task → Station Bar: start this class**. Use either method once. If you already started examples manually, stop them in their terminals with **Ctrl+C** first. Closing their browser tabs does not stop their servers.

The first run prepares the frontend environment (`.venv-frontend`) and the separate ORM environment (`extensions/orm/.venv`). It may take a few minutes to install dependencies. Later runs reuse them. Nothing is installed into the system Python. The launcher does not pull Git changes or reset your saved orders.

Wait for the **Ready** messages and the list of browser links. Keep that terminal open. **Ctrl+C stops the servers started by this launcher; your saved data stays.** An occupied port is reported instead of stopping an existing process. Errors are printed with the relevant log path under `.classroom/logs/`.

## Which tab do I use?

| Port / label | Use it for | Saved data |
|---|---|---|
| **8002 — Recap: SQLite ORM** | Open `/docs` to create an order during the database recap. | `extensions/orm/data/bar.sqlite` |
| **8090 — Styles: Custom CSS / Bootstrap** | Open the prepared styling comparison. | No orders saved. |
| **8080 — 1: Static prototype** | Submit and reload to see what a browser-only prototype loses. | Simulated result only. |
| **8081 — 2: Browser + API** | Inspect the request in Network, then read back the order. | Calls the JSON API on8000. |
| **8082 — 3: Jinja pages** | Compare server-rendered HTML and form navigation. | Calls the same JSON API on8000. |
| **8000 — API: JSON storage** | Open `/docs` to inspect/change the backend used by the two connected frontends. | `solution/data.json` |

**The SQLite recap and JSON frontend examples use separate data.** Creating an order on8081 or8082 does not change `bar.sqlite`. Port8001 belongs to an earlier starter exercise and is not launched for this class.

In Codespaces, use the printed HTTPS links or **Ports → Open in Browser**, keeping visibility **Private**. If a port is missing, add its number in Ports. A forwarded port alone does not mean a server is running. On your laptop, the launcher instead prints local `http://127.0.0.1` links.

## Inspect the SQLite changes

1. Start the launcher and wait for **8002 Ready**. Startup creates `extensions/orm/data/bar.sqlite` and its tables if they do not exist. The generated `data/` directory is Git-ignored, so it is absent from a fresh clone. Refresh Explorer if it has not appeared yet.
2. Check that **SQLite Viewer by qwtel** (`qwtel.sqlite-viewer`) is installed. New Codespaces include it through the devcontainer configuration; in an existing Codespace, install the workspace recommendation once from Extensions. A read-only viewer is sufficient; installing it is separate from installing Python packages.
3. Open `extensions/orm/data/bar.sqlite` with SQLite Viewer. Select `menu_item`, `bar_order` or `order_line`. If you intentionally configured `BAR_ORM_DB`, use the file printed by the launcher instead.
4. In `/docs` on **8002**, execute **POST /orders**, using an available menu-item ID. For the untouched seed data:

   ```json
   {"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
   ```

5. **Refresh or reopen SQLite Viewer**. Match the returned ID to `bar_order.id` and `order_line.order_id`: one order row, one line with quantity2. A rejected order adds neither. Existing changes to menu availability can cause a rejection; inspect the response first.

If the viewer is unavailable, run this read-only inspection in another terminal (Codespaces):

```sh
extensions/orm/.venv/bin/python extensions/orm/inspect_data.py
```

## Smaller runs and restart

```sh
python start_class.py --only orm       # Just the SQLite recap
python start_class.py --only frontend  # JSON API, interfaces and styling comparison
python start_class.py --setup-only     # Prepare environments ahead of class
```

Do not run these alongside another launcher using the same ports. After Ctrl+C, run the same command again to restart with existing data. Optional overrides `BAR_DATA_FILE` and `BAR_ORM_DB` are respected. No reset, delete, automatic Git operation or container rebuild is performed.

Port labels are supplied in both `.devcontainer/devcontainer.json` and the repository's `.vscode/settings.json`. New Codespaces use the container defaults; the workspace settings also provide labels after pulling into an existing Codespace. If the Ports view still shows an old custom label, right-click it and choose **Set Port Label**, or reload the VS Code window. Keep your existing processes/data; a label change does not require recreating the Codespace. [GitHub port guidance](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).

For individual commands and code explanations, use the existing [frontend guide](../extensions/frontend/README.md#1-update-and-prepare-once) or [ORM guide](../extensions/orm/README.md#run-in-your-codespace). These remain useful when adapting one example to your own project. This launcher is for the prepared teaching examples, not a required project architecture or a production deployment tool.
