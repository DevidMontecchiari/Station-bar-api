"""Browser workflow checks: login, role policy, CSRF and logout, with temporary data."""
import re
import tempfile
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
from extensions.security.accounts import Account, AccountStore, password_hash
from extensions.security.app import create_app
from extensions.security.auth import TokenRegistry
from extensions.security.pages import COOKIE


class LoginChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash = password_hash.hash("test-password-only")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "menu.json"
        self.accounts = AccountStore([Account("user", "user", self.hash), Account("admin", "admin", self.hash)])
        self.app = create_app(self.data, TokenRegistry(), self.accounts)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def csrf(self, response):
        return re.search(r'name="csrf" value="([^"]+)"', response.text)[1]

    def login(self, name="user"):
        page = self.client.get("/login")
        return self.client.post("/login", data={"username": name, "password": "test-password-only", "csrf": self.csrf(page)})

    def test_user_and_admin_views_and_direct_access_denial(self):
        user_page = self.login()
        self.assertEqual(user_page.status_code, 200)
        self.assertNotIn('href="/admin"', user_page.text)
        self.assertEqual(self.client.get("/admin").status_code, 403)
        self.login("admin")
        page = self.client.get("/admin")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Who can do what?", page.text)
        self.assertNotIn(self.hash, page.text)
        self.assertNotIn("test-password-only", page.text)

    def test_admin_create_is_visible_in_user_menu(self):
        self.login("admin")
        page = self.client.get("/admin")
        result = self.client.post("/admin/menu-items", data={"csrf": self.csrf(page), "name": "Coaching tea", "price": "4.50"})
        self.assertEqual(result.status_code, 200)
        self.assertIn("Menu item saved", result.text)
        self.login("user")
        self.assertIn("Coaching tea", self.client.get("/menu").text)

    def test_client_role_and_direct_post_cannot_escalate(self):
        page = self.login()
        before = self.data.read_bytes()
        result = self.client.post("/admin/menu-items", data={"csrf": self.csrf(page), "name": "Forbidden", "price": "4", "role": "admin"}, headers={"X-Role": "admin"})
        self.assertEqual(result.status_code, 403)
        self.assertEqual(self.data.read_bytes(), before)

    def test_form_changes_require_session_bound_csrf(self):
        self.login("admin")
        before = self.data.read_bytes()
        for value in ("wrong-token", ""):
            self.assertEqual(self.client.post("/admin/menu-items", data={"csrf": value, "name": "Blocked", "price": "4"}).status_code, 403)
        self.assertEqual(self.data.read_bytes(), before)
        self.assertEqual(self.client.post("/logout", data={"csrf": "wrong"}).status_code, 403)
        self.assertEqual(self.client.get("/admin").status_code, 200)

    def test_login_csrf_and_generic_password_errors(self):
        self.assertEqual(self.client.post("/login", data={"username": "admin", "password": "test-password-only", "csrf": "wrong"}).status_code, 403)
        page = self.client.get("/login")
        for name in ("user", "unknown"):
            result = self.client.post("/login", data={"username": name, "password": "bad", "csrf": self.csrf(page)})
            self.assertEqual(result.status_code, 401)
            self.assertIn("Username or password not recognised", result.text)

    def test_repeated_failed_login_is_limited(self):
        page = self.client.get("/login")
        payload = {"username": "user", "password": "bad", "csrf": self.csrf(page)}
        for _ in range(5):
            self.assertEqual(self.client.post("/login", data=payload).status_code, 401)
        self.assertEqual(self.client.post("/login", data=payload).status_code, 429)

    def test_session_rotates_on_login_and_revokes_on_logout(self):
        page = self.client.get("/login")
        old = self.client.cookies.get(COOKIE)
        page = self.client.post("/login", data={"username": "user", "password": "test-password-only", "csrf": self.csrf(page)})
        current = self.client.cookies.get(COOKIE)
        self.assertNotEqual(old, current)
        self.assertIsNone(self.app.state.sessions.get(old))
        self.client.post("/logout", data={"csrf": self.csrf(page)})
        self.assertIsNone(self.app.state.sessions.get(current))
        self.client.cookies.set(COOKIE, current)
        self.assertEqual(self.client.get("/menu", follow_redirects=False).status_code, 303)

    def test_expired_session_and_restart_require_login(self):
        self.login()
        token = self.client.cookies.get(COOKIE)
        self.app.state.sessions.clock = lambda: 10**12
        self.assertEqual(self.client.get("/menu", follow_redirects=False).headers["location"], "/login")
        restarted = create_app(self.data, TokenRegistry(), self.accounts)
        self.assertIsNone(restarted.state.sessions.get(token))

    def test_server_assignment_is_resolved_on_each_request(self):
        self.login("admin")
        self.accounts.accounts["admin"] = Account("admin", "user", self.hash)
        self.assertEqual(self.client.get("/admin").status_code, 403)

    def test_safe_rendering_validation_and_cookie_policy(self):
        self.login("admin")
        page = self.client.get("/admin")
        bad = self.client.post("/admin/menu-items", data={"csrf": self.csrf(page), "name": "Bad", "price": "-1"})
        self.assertEqual(bad.status_code, 422)
        self.client.post("/admin/menu-items", data={"csrf": self.csrf(page), "name": "<script>alert(1)</script>", "price": "1"})
        menu = self.client.get("/menu")
        self.assertIn("&lt;script&gt;", menu.text)
        self.assertNotIn("<script>alert", menu.text)
        self.assertEqual(menu.headers["cache-control"], "no-store")
        with TestClient(create_app(self.data, TokenRegistry(), self.accounts, True), base_url="https://testserver") as secure:
            header = secure.get("/login").headers["set-cookie"]
            for attribute in ("Secure", "HttpOnly", "SameSite=lax"):
                self.assertIn(attribute, header)

    def test_browser_cookie_does_not_become_api_bearer_credential(self):
        self.login("admin")
        self.assertEqual(self.client.get("/whoami").status_code, 401)

    def test_private_files_are_not_served(self):
        for path in ("/.classroom/security-accounts.json", "/.classroom/security-credentials.json", "/templates/login.html", "/accounts.py"):
            self.assertEqual(self.client.get(path).status_code, 404)


if __name__ == "__main__":
    unittest.main()
