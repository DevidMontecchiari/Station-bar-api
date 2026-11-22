"""Trusted account data and role policy, shared by pages and API examples.

The classroom seeds two fictional accounts. Password hashing uses pwdlib's
Argon2 implementation, as in the FastAPI tutorial; no homemade password hash.
Replace AccountStore with your existing user repository when adapting this.
"""
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import tempfile
from threading import RLock
from pwdlib import PasswordHash
from .auth import Principal

ROLE_PERMISSIONS = {
    "user": frozenset(),
    "admin": frozenset({"menu:write"}),
}
password_hash = PasswordHash.recommended()


@dataclass(frozen=True)
class Account:
    username: str
    role: str
    password_hash: str


class AccountStore:
    def __init__(self, accounts, file: Path | None = None):
        self.accounts = {a.username: a for a in accounts}
        self.file = Path(file) if file is not None else None
        self.lock = RLock()  # One server process; use a database for multiple workers.
        self.dummy_hash = password_hash.hash("unused-unknown-account-password")

    def register(self, username, password):
        """Self-registration always creates a user. Role is not a form input."""
        # Keep one clear identifier spelling; passwords are never trimmed.
        username = username.strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,31}", username):
            raise ValueError("Use 3–32 letters, numbers, dots, underscores or hyphens; start with a letter or number.")
        if not 15 <= len(password) <= 128:
            raise ValueError("Use a password of 15–128 characters. Spaces are allowed.")
        with self.lock:
            if username in self.accounts:
                raise ValueError("Choose a different username.")
            account = Account(username, "user", password_hash.hash(password))
            updated = {**self.accounts, username: account}
            # A failed save must not create a working, but unsaved, login.
            self._persist(updated)
            self.accounts = updated
        return account

    def _persist(self, accounts):
        if self.file is None:  # In-memory store used by isolated tests.
            return
        self.file.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix=".accounts-", suffix=".tmp", dir=self.file.parent)
        temporary = Path(name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump([asdict(a) for a in accounts.values()], stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.file)
        finally:
            temporary.unlink(missing_ok=True)

    def authenticate(self, username, password):
        account = self.accounts.get(username)
        # Check a hash even when the username does not exist.
        valid = password_hash.verify(password, account.password_hash if account else self.dummy_hash)
        return account if account and valid else None

    def principal(self, username):
        account = self.accounts.get(username)
        if account is None:
            return None
        return Principal(account.username, ROLE_PERMISSIONS.get(account.role, frozenset()))

    def assignments(self):
        # The admin view receives no password hashes or credentials.
        with self.lock:
            return [{"username": a.username, "role": a.role,
                     "permissions": sorted(self.principal(a.username).permissions)}
                    for a in self.accounts.values()]
