"""Registration, persistence and privilege-boundary checks with fictional data."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from extensions.security.accounts import Account, AccountStore, password_hash
from extensions.security.app import create_app
from extensions.security.auth import TokenRegistry
from extensions.security.pages import COOKIE

PASSWORD = "a fictional café passphrase"


class SignupChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_hash = password_hash.hash("seed-test-password")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = Path(self.tmp.name) / "accounts.json"
        self.data = Path(self.tmp.name) / "menu.json"
        seeds = [Account(name, name, self.seed_hash) for name in ("user", "admin")]
        self.file.write_text(json.dumps([asdict(a) for a in seeds]), encoding="utf-8")
        self.accounts = AccountStore(seeds, file=self.file)
        self.app = create_app(self.data, TokenRegistry(), self.accounts)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def csrf(self, page):
        return re.search(r'name="csrf" value="([^"]+)"', page.text)[1]

    def signup(self, **changes):
        page = self.client.get("/signup")
        data = {"username": "new-guest", "password": PASSWORD,
                "confirm_password": PASSWORD, "csrf": self.csrf(page)}
        data.update(changes)
        return self.client.post("/signup", data=data)

    def login(self, username="new-guest", password=PASSWORD, client=None):
        client = client or self.client
        page = client.get("/login")
        return client.post("/login", data={"username": username, "password": password, "csrf": self.csrf(page)})

    def test_signup_then_login_and_no_admin_privileges(self):
        self.assertIn('href="/signup"', self.client.get("/login").text)
        result = self.signup(role="admin", permissions="menu:write")
        self.assertIn("Account created", result.text)
        # Creating an account is not authentication.
        self.assertEqual(self.client.get("/menu", follow_redirects=False).status_code, 303)
        page = self.login()
        self.assertEqual(page.status_code, 200)
        self.assertIn("new-guest", page.text)
        self.assertNotIn('href="/admin"', page.text)
        self.assertEqual(self.accounts.accounts["new-guest"].role, "user")
        self.assertEqual(self.accounts.principal("new-guest").permissions, frozenset())
        before = self.data.read_bytes()
        self.assertEqual(self.client.get("/admin").status_code, 403)
        denied = self.client.post("/admin/menu-items", data={"csrf": self.csrf(page), "role": "admin", "name": "No", "price": "1"})
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(self.data.read_bytes(), before)

    def test_only_hash_is_saved_and_login_survives_restart(self):
        self.signup()
        saved = self.file.read_text(encoding="utf-8")
        self.assertNotIn(PASSWORD, saved)
        self.assertIn("$argon2id$", saved)
        self.assertEqual(set(json.loads(saved)[-1]), {"username", "role", "password_hash"})
        self.login()
        old_cookie = self.client.cookies.get(COOKIE)
        store = AccountStore([Account(**a) for a in json.loads(saved)], file=self.file)
        restarted = create_app(self.data, TokenRegistry(), store)
        self.assertIsNone(restarted.state.sessions.get(old_cookie))
        with TestClient(restarted) as client:
            self.assertEqual(self.login(client=client).status_code, 200)
            self.assertIn("new-guest", client.get("/menu").text)

    def test_case_normalisation_cannot_overwrite_existing_admin(self):
        before = self.file.read_bytes()
        result = self.signup(username=" Admin ")
        self.assertEqual(result.status_code, 422)
        self.assertEqual(self.file.read_bytes(), before)
        self.assertIsNotNone(self.accounts.authenticate("admin", "seed-test-password"))
        self.assertEqual(self.signup(username=" New.Guest ").status_code, 200)
        self.assertIn("new.guest", self.accounts.accounts)
        before = self.file.read_bytes()
        self.assertEqual(self.signup(username="NEW.GUEST").status_code, 422)
        self.assertEqual(self.file.read_bytes(), before)

    def test_confirmation_and_password_bounds_never_echo_password(self):
        before = self.file.read_bytes()
        for password, confirm in [(PASSWORD, "mismatch"), ("short", "short"), ("x"*129, "x"*129)]:
            response = self.signup(password=password, confirm_password=confirm)
            self.assertEqual(response.status_code, 422)
            self.assertNotIn('value="'+password+'"', response.text)
            self.assertEqual(self.file.read_bytes(), before)
        response = self.signup(username="<script>alert(1)</script>")
        self.assertEqual(response.status_code, 422)
        self.assertNotIn("<script>alert", response.text)
        self.assertEqual(self.file.read_bytes(), before)

    def test_signup_requires_csrf_from_this_anonymous_session(self):
        before = self.file.read_bytes()
        self.assertEqual(self.signup(csrf="wrong").status_code, 403)
        page = self.client.get("/signup")
        with TestClient(self.app) as other:
            other.get("/signup")
            response = other.post("/signup", data={"username": "new-guest", "password": PASSWORD,
                                  "confirm_password": PASSWORD, "csrf": self.csrf(page)})
            self.assertEqual(response.status_code, 403)
        self.assertEqual(self.file.read_bytes(), before)

    def test_success_retires_anonymous_session_and_does_not_issue_api_token(self):
        page = self.client.get("/signup")
        token = self.client.cookies.get(COOKIE)
        result = self.client.post("/signup", data={"username": "new-guest", "password": PASSWORD,
                                 "confirm_password": PASSWORD, "csrf": self.csrf(page)}, follow_redirects=False)
        self.assertEqual(result.status_code, 303)
        self.assertEqual(result.headers["location"], "/login?registered=1")
        self.assertIsNone(self.app.state.sessions.get(token))
        self.assertEqual(self.client.get("/whoami").status_code, 401)

    def test_signed_in_account_cannot_register_another_account(self):
        menu = self.login("admin", "seed-test-password")
        self.assertEqual(self.client.get("/signup", follow_redirects=False).headers["location"], "/menu")
        before = self.file.read_bytes()
        response = self.client.post("/signup", data={"username": "another", "password": PASSWORD,
                                    "confirm_password": PASSWORD, "csrf": self.csrf(menu)})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.file.read_bytes(), before)

    def test_registration_attempt_limit_is_not_bypassed_by_changing_username(self):
        for n in range(5):
            self.assertEqual(self.signup(username=f"guest{n}", confirm_password="wrong").status_code, 422)
        self.assertEqual(self.signup(username="different").status_code, 429)
        self.app.state.signup_attempts.clock = lambda: 10**12
        self.assertEqual(self.signup(username="after-wait").status_code, 200)

    def test_failed_disk_save_preserves_old_file_and_does_not_create_login(self):
        before = self.file.read_bytes()
        with patch("extensions.security.accounts.os.replace", side_effect=OSError("test failure")):
            response = self.signup()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(self.file.read_bytes(), before)
        self.assertIsNone(self.accounts.authenticate("new-guest", PASSWORD))
        self.assertEqual(list(self.file.parent.glob(".accounts-*.tmp")), [])
        self.assertNotIn("test failure", response.text)

    def test_concurrent_duplicate_registration_creates_one_account(self):
        def attempt(_):
            try:
                return self.accounts.register("same-guest", PASSWORD).username
            except ValueError:
                return "duplicate"
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, range(2)))
        self.assertCountEqual(results, ["same-guest", "duplicate"])
        self.assertEqual(len(json.loads(self.file.read_text())), 3)

    def test_signup_cookie_and_response_headers_support_https(self):
        with TestClient(create_app(self.data, TokenRegistry(), self.accounts, True), base_url="https://testserver") as client:
            page = client.get("/signup")
            for value in ("Secure", "HttpOnly", "SameSite=lax"):
                self.assertIn(value, page.headers["set-cookie"])
            self.assertEqual(page.headers["cache-control"], "no-store")
            self.assertIn("form-action 'self'", page.headers["content-security-policy"])


if __name__ == "__main__":
    unittest.main()
