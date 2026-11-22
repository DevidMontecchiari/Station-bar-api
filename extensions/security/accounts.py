"""Trusted account data and role policy, shared by pages and API examples.

The classroom seeds two fictional accounts. Password hashing uses pwdlib's
Argon2 implementation, as in the FastAPI tutorial; no homemade password hash.
Replace AccountStore with your existing user repository when adapting this.
"""
from dataclasses import dataclass
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
    def __init__(self, accounts):
        self.accounts = {a.username: a for a in accounts}
        self.dummy_hash = password_hash.hash("unused-unknown-account-password")

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
        return [{"username": a.username, "role": a.role,
                 "permissions": sorted(self.principal(a.username).permissions)}
                for a in self.accounts.values()]
