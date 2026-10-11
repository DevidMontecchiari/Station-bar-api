# Create your own Codespace

**No local installation is needed for the current class.** Use your browser and GitHub account with Codespaces access; Python, VS Code and the project dependencies are provided in the cloud environment.

Sign in to your own GitHub account. Open the class repository (or your fork), choose **Code > Codespaces**, and create or resume **your own workspace**. GitHub clones the repository into it automatically; you do not need a local clone first. The supplied `.devcontainer` configuration prepares Python and dependencies.

The lecturer's Codespace and its private API address belong to the lecturer's environment. Use your own Codespace and the port address it provides. If you want an independent repository for saving your changes, fork the class repository first.

Run from the **repository root**, where `run.py` and `check.py` are located; do not change into `starter/` or `solution/` to run these commands. The runner selects the application folder for you.

An API keeps its terminal busy while running. Use **Terminal > New Terminal** for another command: one terminal for the reference API, one for the starter API, and a free terminal for checks. The checks can run without either API running.

| Purpose | Command | Browser |
| --- | --- | --- |
| Explore the complete reference | `python run.py solution --host 0.0.0.0` | Ports: 8000, then /docs |
| Edit the starter | `python run.py starter --host 0.0.0.0 --port 8001 --reload` | Ports: 8001, then /docs |
| Check the starter | `python check.py starter` | Terminal results |
| Check the reference | `python check.py solution --full` | Terminal results |

**Why 8000 and 8001?** These are two running versions of the backend in the same Codespace: the complete reference on 8000 and your starter on 8001. Separate ports let you compare them while both run; starting both on the same address and port with these commands would fail. Each port has its own forwarded URL, so use the 8001 URL when testing your changes. You can reuse a port if you stop the other API first.

Use **Ports > Open in Browser** and append /docs to the generated address. Keep the port private and use the browser signed in to GitHub. Its hostname belongs to your codespace; it is not localhost on your laptop.

For the classroom task, follow [exercise 2](../exercises/02-create-order.md): inspect the initial test results, edit the marked starter handler, check it, then try it in `/docs`.

## If something does not open

- Wait for environment creation to finish before running the API.
- Check that you are in the repository root and the API process is running. If Python cannot find `run.py`, use the terminal opened at the repository root.
- If the terminal is displaying API logs, leave it running and use **Terminal > New Terminal** for checks.
- If port 8001 is already in use, find the terminal running the starter; stop that process with Ctrl+C before starting it again.
- If a port is missing, add 8000 or 8001 in the Ports panel.
- A 404 at the root address is expected: append /docs.
- A 501 from the unfinished starter's POST /orders is intentional. Complete the marked handler.
- If GitHub access or Codespaces availability blocks setup, follow the shared demonstration and use the local Python route later. Do not install Docker during the exercise.

## Later: Postman and frontend connections

The design and deployment classes will revisit two ways to connect external clients to this application:

- **Local execution:** follow [local Python setup](python-setup.md), then point Postman or your frontend at the local API address, such as `http://127.0.0.1:8000`. This setup is optional for later.
- **Codespaces forwarding:** use the forwarded URL as the API base address. A private remote port requires GitHub authentication. For the later demonstration, **Ports > right-click the port > Port Visibility > Public** makes it accessible without that GitHub authentication, if your account or organisation policy permits it. Anyone with the URL can then access the running API.

Keep ports **Private** for the current exercise and use `/docs` in your signed-in browser. Public forwarding is a development demonstration, not a permanent deployment. See [GitHub's port-forwarding documentation](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).

## Saved data and work

Each version saves its own ignored data.json. Stopping and restarting its API preserves the data. Tests use temporary data.

For a fresh demonstration, stop the corresponding API, run `python solution/reset_data.py --confirm` or `python starter/reset_data.py --confirm`, then start that API again. Reset replaces the demonstration data.

Save work in your own repository or fork if you want to keep changes beyond the reference exercise. Stop the codespace when finished; closing its browser tab does not stop the compute session.

[Learning path](../README.md) | [Creating a Codespace](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository) | [GitHub port forwarding](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace)
