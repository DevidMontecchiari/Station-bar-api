"""One command for the security lesson: python start_security.py.

Separate environment and data; reuse existing process/port helpers. Does not
start other examples, reset data, stop unrelated processes or run Git.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import venv
from start_class import ClassSession, Service, check_ports, environment_python, requirement_files, show_links

ROOT = Path(__file__).resolve().parent


def prepare_environment():
    folder = ROOT / ".venv-security"
    python = environment_python(folder)
    if not folder.exists():
        print("Preparing .venv-security (first run)...", flush=True)
        venv.EnvBuilder(with_pip=True).create(folder)
    if not python.is_file():
        raise RuntimeError(".venv-security has no Python for this OS. Rename it as a backup and retry.")
    requirements = ROOT / "extensions/security/requirements.txt"
    pins = {}
    for file in requirement_files(ROOT, requirements):
        for line in file.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                name, version = line.split("==", 1)
                pins[name] = version
    probe = ("import importlib.metadata as m,json; " +
             f"wanted=json.loads({json.dumps(pins)!r}); " +
             "assert all(m.version(k)==v for k,v in wanted.items()); import fastapi,uvicorn,httpx,jinja2,multipart,pwdlib,argon2")
    if subprocess.run([str(python), "-c", probe], capture_output=True).returncode:
        print("Installing security requirements into .venv-security...", flush=True)
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(requirements)], cwd=ROOT, check=True)
        if subprocess.run([str(python), "-c", probe], capture_output=True).returncode:
            raise RuntimeError("Security dependency check failed; see installation output.")
    return python


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--setup-only", action="store_true")
    mode.add_argument("--check", action="store_true", help="Checks use temporary data; no server stays running")
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument("--host", choices=["127.0.0.1", "0.0.0.0"],
                        default="0.0.0.0" if os.environ.get("CODESPACE_NAME") or os.environ.get("CODESPACES") == "true" else "127.0.0.1")
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    session = None
    previous = signal.getsignal(signal.SIGTERM)
    def stop(_signal, _frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        python = environment_python(ROOT / ".venv-security")
        planned = [Service("Security | user + admin login", args.port,
                   [str(python), str(ROOT / "extensions/security/run.py"), "--host", args.host, "--port", str(args.port)],
                   "/login", "/openapi.json")]
        if not args.setup_only and not args.check:
            check_ports(planned)
        prepare_environment()
        if args.setup_only:
            print("Ready. Run python start_security.py for the lesson.")
            return 0
        if args.check:
            return subprocess.run([str(python), "-m", "unittest", "discover", "-s", "extensions/security/tests", "-v"], cwd=ROOT).returncode
        print("STATION BAR | Security lesson. Existing JSON/ORM/frontend examples stay separate.", flush=True)
        session = ClassSession(ROOT, planned)
        session.start()
        show_links(planned)
        print("\nOpen .classroom/security-credentials.json locally for user/admin passwords.\n"
              "Browser: sign in at /login. Use separate browser profiles for simultaneous views.\n"
              "Optional API checks: /docs > Authorize > paste ONLY the account's token value.\n"
              "Data: extensions/security/data/menu.json (separate; retained on restart).\n"
              "Browser sessions expire after one hour; restart signs everyone out but keeps accounts/data.\n"
              "Follow exercises/06-security.md. Keep this terminal open; Ctrl+C stops this run.", flush=True)
        session.wait()
    except KeyboardInterrupt:
        print("\nStopping the security example...", flush=True)
        return 0
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Could not start security example: {error}", file=sys.stderr, flush=True)
        return 1
    finally:
        if session is not None:
            session.close()
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    raise SystemExit(main())
