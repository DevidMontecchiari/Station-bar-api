# Container controls

Run commands from the repository root. Docker must be running with Linux containers. The image supplies Python and dependencies; your laptop does not need a separate Python installation for this route.

| Purpose | Command | Open |
| --- | --- | --- |
| Explore the reference | `docker compose up --build` | http://localhost:8000/docs |
| Work on the starter | `docker compose up --build starter` | http://localhost:8001/docs |
| Start both | `docker compose --profile exercise up --build` | Both addresses |
| Check your handler | `docker compose run --rm starter python check.py starter` | Terminal results |
| Check the reference | `docker compose run --rm solution python check.py solution --full` | Terminal results |
| Inspect running services | `docker compose --profile exercise ps` | Terminal |
| Stop both, retaining data | `docker compose --profile exercise down` | Data retained |

The starter folder is mounted from your working copy, so editing Python there reloads the starter API. The reference is copied into its image; rebuild it after changing solution code. Both run the same logical layers within a single backend container.

## Reset one demonstration

Stop the chosen service first. Reset replaces only that service's saved demonstration data with its seed; it does not edit source files.

```sh
docker compose stop starter
docker compose run --rm starter python starter/reset_data.py --confirm
docker compose up starter
```

For the reference, replace every `starter` above with `solution`.

The two services have separate Docker volumes. A normal stop, restart or `down` retains them. Container data and local Python data are separate.

## A port is already used

Stop the other application or choose another port. In PowerShell, for example:

```powershell
$env:BAR_SOLUTION_PORT = "8010"
docker compose up --build
```

Then open http://localhost:8010/docs. The corresponding starter setting is `BAR_STARTER_PORT`.

## Inside VS Code Dev Containers

Choose **Dev Containers: Reopen in Container**. Run the API with `python run.py solution --host 0.0.0.0`; run checks with `python check.py starter`. There is no need for Docker inside the development container. Keep forwarded ports private if using a hosted environment.

## PowerShell cannot find Docker

If PowerShell says `docker` is not recognised, it cannot find the Docker CLI. Close and reopen VS Code or your terminal after installation. Existing terminals inherit the environment of the application that opened them.

For a per-user Docker Desktop installation on Windows, this refreshes the current PowerShell session when the CLI exists in the usual location:

```powershell
$dockerBin = Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin'
if (Test-Path (Join-Path $dockerBin 'docker.exe')) {
    $env:Path += ";$dockerBin"
}
docker --version
docker compose version
```

If Docker is installed elsewhere, use its actual `resources\bin` folder. Add that folder to your Windows **user Path** for future sessions if it is missing. This fixes command discovery; Docker Desktop must also be running before Compose can start containers. Complete any restart requested during WSL installation first. See [PowerShell environment scopes](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_environment_variables).

## If startup fails

- Check `docker version` and `docker compose version`. A client version without a reachable server usually means Docker Desktop has not started or its WSL backend needs attention.
- The first build needs internet access to download the Python image and packages.
- On Windows, complete any WSL installation and restart requested by Windows before starting Docker.
- Inspect `docker compose logs solution` or `docker compose logs starter`.
- Use [local Python setup](python-setup.md) if containers are unavailable.

Configuration follows the [FastAPI container guide](https://fastapi.tiangolo.com/deployment/docker/) and [Compose profile behaviour](https://docs.docker.com/compose/how-tos/profiles/). Only the starter uses the exercise profile; explicitly requesting that service starts it. [Localhost port publishing](https://docs.docker.com/engine/network/port-publishing/) keeps this classroom API off the local network.
