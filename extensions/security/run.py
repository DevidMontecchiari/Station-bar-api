"""Run using the security environment; normally use python start_security.py."""
import argparse
from datetime import datetime, timezone
import json
import os
import secrets
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    import uvicorn
    from extensions.security.auth import TokenRegistry
    from extensions.security.accounts import Account, AccountStore, password_hash
    from extensions.security.app import create_app
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", choices=["127.0.0.1", "0.0.0.0"])
    parser.add_argument("--port", default=8003, type=int)
    parser.add_argument("--secure-cookies", action="store_true", help="Require HTTPS for browser cookies")
    args = parser.parse_args()
    registry = TokenRegistry()
    data_file = Path(os.environ.get("BAR_SECURITY_DATA", ROOT / "extensions/security/data/menu.json"))
    credential_file = Path(os.environ.get("BAR_SECURITY_CREDENTIALS", ROOT / ".classroom/security-credentials.json"))
    account_file = credential_file.with_name("security-accounts.json")
    credential_file.parent.mkdir(parents=True, exist_ok=True)
    entries = json.loads(credential_file.read_text(encoding="utf-8")) if credential_file.exists() else {}
    if account_file.exists():
        accounts = AccountStore([Account(**row) for row in json.loads(account_file.read_text(encoding="utf-8"))])
    else:
        rows = []
        entries = {}
        for name, role in [("user", "user"), ("admin", "admin")]:
            password = secrets.token_urlsafe(16)
            rows.append({"username": name, "role": role, "password_hash": password_hash.hash(password)})
            entries[name] = {"username": name, "password": password, "role": role}
        fd = os.open(account_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(rows, stream, indent=2)
        accounts = AccountStore([Account(**row) for row in rows])
    for name in accounts.accounts:
        principal = accounts.principal(name)
        token, expires = registry.issue(principal)
        entries[name] = {**entries.get(name, {}), "username": name, "token": token,
                         "role": accounts.accounts[name].role, "permissions": sorted(principal.permissions),
                         "expires_utc": datetime.fromtimestamp(expires, timezone.utc).isoformat()}
    # Local bootstrap file, never served by HTTP; OS permissions vary on Windows.
    fd = os.open(credential_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(entries, stream, indent=2)
        stream.write("\n")
    print(f"Demo accounts: {credential_file} (passwords retained; API tokens rotate on restart)", flush=True)
    print(f"Security data: {data_file}", flush=True)
    secure = args.secure_cookies or bool(os.environ.get("CODESPACE_NAME")) or os.environ.get("CODESPACES") == "true"
    uvicorn.run(create_app(data_file, registry, accounts, secure), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
