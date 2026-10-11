# Local Python setup

**Optional setup for later classes.** The current exercise uses [Codespaces in your browser](codespaces.md) and requires no local installation. We will revisit local execution in the design and deployment material.

Use Python 3.14, matching the tested teaching environment, and VS Code (or another editor). Docker and Codespaces are not needed for this route.

## Get your own local copy

1. Open the class repository on GitHub. Choose **Code > Local** and copy its HTTPS clone URL.
2. In VS Code, run **Git: Clone** from the Command Palette, paste that URL and open the cloned folder. Git must be installed for cloning. Alternatively choose **Code > Download ZIP**, extract it and open the extracted folder in VS Code.
3. Open a terminal in that folder. You should see `run.py`, `check.py`, `solution/` and `starter/`. Use this repository root for the commands below.

If you want to push your changes to your own GitHub repository, fork first and clone your fork. A downloaded ZIP is sufficient to run and edit the exercise locally.

## Install dependencies and run

Create a Python virtual environment:

```sh
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in PowerShell, or `source .venv/bin/activate` on macOS/Linux. Then:

```sh
python -m pip install -r solution/requirements-test.txt
python run.py solution
```

Open http://127.0.0.1:8000/docs. In another terminal with the same environment activated:

```sh
python run.py starter --port 8001 --reload
```

Open http://127.0.0.1:8001/docs for your starter. Run `python check.py starter` to check your handler, or `python check.py solution --full` for all reference checks. No server needs to be running for the checks; they use temporary data.

Stop a server with Ctrl+C. To restore one version's seed data, stop that server and run `python starter/reset_data.py --confirm` or `python solution/reset_data.py --confirm`. Each version has its own ignored data.json.

Return to the [learning path](../README.md#start-here).
