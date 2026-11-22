"""Small server-side session store for this single-process teaching example.

The cookie contains a random identifier, never a role or password. A production
multi-worker deployment needs a shared store and an appropriate lifecycle.
"""
from dataclasses import dataclass
from hashlib import sha256
import secrets
import time


@dataclass
class Session:
    username: str | None
    csrf: str
    expires: float


class SessionStore:
    def __init__(self, clock=time.time):
        self.clock = clock
        self.records = {}

    def issue(self, username=None):
        self.records = {k: v for k, v in self.records.items() if v.expires > self.clock()}
        if len(self.records) >= 1000:
            self.records.pop(next(iter(self.records)))
        token = secrets.token_urlsafe(32)
        session = Session(username, secrets.token_urlsafe(32), self.clock() + (3600 if username else 600))
        self.records[sha256(token.encode()).hexdigest()] = session
        return token, session

    def get(self, token):
        key = sha256((token or "").encode()).hexdigest()
        value = self.records.get(key)
        if value and value.expires > self.clock():
            return value
        self.records.pop(key, None)
        return None

    def revoke(self, token):
        self.records.pop(sha256((token or "").encode()).hexdigest(), None)


class LoginAttempts:
    """Bound repeated failed attempts per username; replace for public deployment."""
    def __init__(self, clock=time.time):
        self.clock, self.failed = clock, {}

    def blocked(self, username):
        self.failed = {k: v for k, v in self.failed.items() if v[1] > self.clock()}
        return self.failed.get(username, (0, 0))[0] >= 5

    def failure(self, username):
        if username not in self.failed and len(self.failed) >= 1000:
            self.failed.pop(next(iter(self.failed)))
        count, until = self.failed.get(username, (0, self.clock() + 60))
        self.failed[username] = (count + 1, until)

    def clear(self, username):
        self.failed.pop(username, None)
