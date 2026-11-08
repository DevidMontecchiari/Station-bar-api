"""Start the prepared frontend class examples from one terminal.

Standard-library entry point: python start_class.py
Creates/reuses two isolated environments; never resets data or stops other apps.
Keep this terminal open. Ctrl+C stops only the processes started here.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import venv

ROOT = Path(__file__).resolve().parent
HTTP = build_opener(ProxyHandler({}))  # Local readiness checks must not use a proxy.


@dataclass(frozen=True)
class Service:
    name: str
    port: int
    command: list[str]
    open_path: str = "/"
    check_path: str = "/"


def environment_python(folder: Path) -> Path:
    return folder / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def requirement_files(root: Path, entry: Path) -> list[Path]:
    """Follow the supplied local -r includes, once, within this repository."""
    found = []

    def visit(path):
        path = path.resolve()
        if not path.is_relative_to(root.resolve()):
            raise RuntimeError("Requirements include a file outside this repository.")
        if path in found:
            return
        found.append(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line.startswith("-r "):
                visit(path.parent / line[3:].strip())

    visit(entry)
    return found


def prepare_environment(root: Path, folder: Path, requirements: Path) -> Path:
    python = environment_python(folder)
    if not folder.exists():
        print(f"Preparing {folder.relative_to(root)} (first run)...", flush=True)
        venv.EnvBuilder(with_pip=True).create(folder)
    if not python.is_file():
        raise RuntimeError(f"{folder} exists but has no usable Python for this OS. "
                           "Rename it as a backup, then run this launcher again.")
    files = requirement_files(root, requirements)
    fingerprint = hashlib.sha256(b"".join(p.read_bytes() for p in files)).hexdigest()
    pins = {}
    for path in files:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                name, version = line.split("==", 1)
                pins[name.strip()] = version.strip()
    probe = ("import importlib.metadata as m,json; "
             f"wanted=json.loads({json.dumps(pins)!r}); "
             "assert all(m.version(k)==v for k,v in wanted.items()); "
             "import fastapi,uvicorn; " +
             ("import sqlmodel,sqlalchemy" if "sqlmodel" in pins else "import jinja2,httpx,python_multipart"))
    stamp = folder / ".classroom-requirements.sha256"
    probe_ok = subprocess.run([str(python), "-c", probe], capture_output=True).returncode == 0
    previous = stamp.read_text().strip() if stamp.exists() else None
    # An existing manually prepared environment can be adopted without downloading again.
    if not probe_ok or (previous is not None and previous != fingerprint):
        print(f"Installing {requirements.relative_to(root)} into {folder.relative_to(root)}...", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(requirements)],
                       cwd=root, check=True)
        if subprocess.run([str(python), "-c", probe], capture_output=True).returncode:
            raise RuntimeError(f"Dependency check failed in {folder}; see the installation output.")
    stamp.write_text(fingerprint + "\n", encoding="utf-8")
    return python


def services(root: Path, interpreters: dict[str, Path], profile: str, host: str,
             offset: int = 0) -> list[Service]:
    """Ports stay fixed for teaching; offset is used only by isolated local tests."""
    result = []
    if profile in ("all", "frontend"):
        python = str(interpreters["frontend"])
        api_port = 8000 + offset
        result.append(Service("JSON API | frontend storage", api_port,
            [python, str(root / "run.py"), "solution", "--port", str(api_port), "--host", host],
            "/docs", "/openapi.json"))
        for variant, port, title in [("static", 8080, "Static prototype | simulated orders"),
                                     ("api-client", 8081, "Browser + API | saved orders"),
                                     ("server-rendered", 8082, "Jinja pages | saved orders")]:
            result.append(Service(title, port + offset,
                [python, str(root / "extensions/frontend/run.py"), variant,
                 "--port", str(port + offset), "--host", host,
                 "--api-url", f"http://127.0.0.1:{api_port}"]))
        # Serve only the comparison folder, not the repository or its data/config files.
        result.append(Service("CSS comparison | custom / Bootstrap", 8090 + offset,
            [python, "-m", "http.server", str(8090 + offset), "--bind", host,
             "--directory", str(root / "extensions/frontend/style-comparison")]))
    if profile in ("all", "orm"):
        result.append(Service("SQLite API | database recap", 8002 + offset,
            [str(interpreters["orm"]), str(root / "extensions/orm/run.py"),
             "--port", str(8002 + offset), "--host", host], "/docs", "/openapi.json"))
    return sorted(result, key=lambda s: s.port)


def check_ports(planned: list[Service]) -> None:
    busy = []
    for service in planned:
        with socket.socket() as probe:
            probe.settimeout(.3)
            if probe.connect_ex(("127.0.0.1", service.port)) == 0:
                busy.append(f"  {service.port}: {service.name}")
                continue
        # A stale socket in TIME_WAIT is not a running server. Any actual bind
        # failure/race is also caught by the child's startup/readiness check.
    if busy:
        raise RuntimeError("These ports are already in use:\n" + "\n".join(busy) +
            "\nStop the old demo in its terminal with Ctrl+C, then try again. "
            "Closing a browser tab or stopping port forwarding does not stop a server. "
            "This launcher has not stopped any existing process.")


class ClassSession:
    """Own just this run's subprocesses, logs and cleanup."""
    def __init__(self, root: Path, planned: list[Service], env=None):
        self.root, self.planned = root, planned
        self.env = dict(os.environ if env is None else env)
        self.env.update(PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
        self.children = []
        self.log_dir = root / ".classroom/logs" / datetime.now().strftime("%Y%m%d-%H%M%S-%f")

    def start(self):
        check_ports(self.planned)
        self.log_dir.mkdir(parents=True)
        try:
            for service in self.planned:
                path = self.log_dir / f"{service.port}.log"
                log = path.open("w", encoding="utf-8")
                try:
                    kwargs = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
                              if os.name == "nt" else {"start_new_session": True})
                    process = subprocess.Popen(service.command, cwd=self.root, env=self.env,
                        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, **kwargs)
                except BaseException:
                    log.close()
                    raise
                self.children.append((service, process, log, path))
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        raise RuntimeError(self.failure(service, path))
                    try:
                        with HTTP.open(f"http://127.0.0.1:{service.port}{service.check_path}", timeout=.5) as response:
                            if response.status == 200 and process.poll() is None:
                                break
                    except (URLError, OSError):
                        pass
                    time.sleep(.15)
                else:
                    raise RuntimeError(f"Port {service.port} did not become ready. " + self.failure(service, path))
                print(f"Ready: {service.port} | {service.name}", flush=True)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def failure(service, path):
        tail = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-12:])
        return f"{service.name} stopped. Log: {path}\n{tail}"

    def wait(self):
        while True:
            for service, process, _, path in self.children:
                if process.poll() is not None:
                    raise RuntimeError(self.failure(service, path))
            time.sleep(.3)

    def close(self):
        # Signal all owned children first, then wait. Never search/kill by port or name.
        for _, process, _, _ in reversed(self.children):
            if process.poll() is None:
                try:
                    process.send_signal(signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGINT)
                except OSError:
                    if process.poll() is None:
                        process.terminate()
        for _, process, log, _ in reversed(self.children):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Use the handle we own, never a system-wide process search.
                # CPython's Windows venv redirector owns a kill-on-close job
                # containing its Python child.
                process.kill()
                process.wait(timeout=5)
            finally:
                log.close()


def show_links(planned: list[Service], env=None):
    env = os.environ if env is None else env
    name = env.get("CODESPACE_NAME")
    domain = env.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
    print("\nOPEN IN BROWSER (keep forwarded ports Private)")
    for service in planned:
        base = f"https://{name}-{service.port}.{domain}" if name else f"http://127.0.0.1:{service.port}"
        print(f"{service.port} | {service.name}\n  {base}{service.open_path}")
    if name:
        print("If a link is not forwarded yet: Ports > Add Port, then Open in Browser.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=["all", "frontend", "orm"], default="all",
                        help="all = this class; frontend omits the SQLite recap; orm starts only SQLite")
    parser.add_argument("--setup-only", action="store_true", help="Prepare environments without starting servers")
    parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"],
                        default="0.0.0.0" if os.environ.get("CODESPACES") == "true" or os.environ.get("CODESPACE_NAME") else "127.0.0.1")
    args = parser.parse_args(argv)
    paths = {"frontend": ROOT / ".venv-frontend", "orm": ROOT / "extensions/orm/.venv"}
    planned = services(ROOT, {k: environment_python(v) for k,v in paths.items()}, args.only, args.host)
    session = None
    old_term = signal.getsignal(signal.SIGTERM)

    def stop(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    try:
        if not args.setup_only:
            check_ports(planned)
        print("STATION BAR | Frontend class + SQLite recap\nExisting data is retained. First setup may download dependencies.", flush=True)
        for name, folder in paths.items():
            if args.only in ("all", name):
                prepare_environment(ROOT, folder, ROOT / f"extensions/{name}/requirements.txt")
        if args.setup_only:
            suffix = "" if args.only == "all" else f" --only {args.only}"
            print(f"Setup complete. Run python start_class.py{suffix} when ready.")
            return 0
        session = ClassSession(ROOT, planned)
        session.start()
        show_links(planned)
        if args.only in ("all", "orm"):
            print("\nSQLite file: " + os.environ.get("BAR_ORM_DB", "extensions/orm/data/bar.sqlite"))
            print("The ORM startup creates this file. Open it with SQLite Viewer; write through /docs on 8002, then refresh the viewer.")
        print(f"\nLogs: {session.log_dir.relative_to(ROOT)}\nKeep this terminal open. Ctrl+C stops this launcher's servers; saved data stays.", flush=True)
        session.wait()
    except KeyboardInterrupt:
        print("\nStopping this class run...", flush=True)
        return 0
    except (RuntimeError, OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"\nCould not start the class:\n{error}", file=sys.stderr, flush=True)
        return 1
    finally:
        if session is not None:
            session.close()
        signal.signal(signal.SIGTERM, old_term)


if __name__ == "__main__":
    raise SystemExit(main())
