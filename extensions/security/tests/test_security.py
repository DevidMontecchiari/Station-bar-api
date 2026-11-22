"""Checks use temporary data and freshly issued fictional credentials."""
import tempfile
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
from extensions.security.app import create_app
from extensions.security.auth import Principal, TokenRegistry

ITEM = {"name": "Workshop tea", "price": 4.0, "currency": "CHF", "available": True}


class SecurityChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "menu.json"
        self.now = 1000.0
        self.tokens = TokenRegistry(clock=lambda: self.now)
        self.viewer, _ = self.tokens.issue(Principal("viewer", frozenset()))
        self.staff, _ = self.tokens.issue(Principal("staff", frozenset({"menu:write"})))
        self.client = TestClient(create_app(self.data, self.tokens))
        self.addCleanup(self.client.close)

    def headers(self, token):
        return {"Authorization": "Bearer " + token}

    def test_public_menu_and_openapi_policy(self):
        self.assertEqual(self.client.get("/menu-items").status_code, 200)
        paths = self.client.get("/openapi.json").json()["paths"]
        self.assertNotIn("security", paths["/menu-items"]["get"])
        self.assertIn("security", paths["/menu-items"]["post"])

    def test_absent_invalid_and_wrong_scheme_are_401_without_writes(self):
        before = self.data.read_bytes()
        for headers in [{}, self.headers("not-a-token"), {"Authorization": "Basic abc"},
                        {"Authorization": "Bearer"}, self.headers(self.staff + "changed")]:
            with self.subTest(headers_present=bool(headers)):
                r = self.client.post("/menu-items", json=ITEM, headers=headers)
                self.assertEqual(r.status_code, 401)
                self.assertEqual(r.headers.get("www-authenticate"), "Bearer")
                self.assertEqual(self.data.read_bytes(), before)

    def test_verified_viewer_is_403_and_data_is_unchanged(self):
        self.assertEqual(self.client.get("/whoami", headers=self.headers(self.viewer)).json(),
                         {"username": "viewer", "permissions": []})
        before = self.data.read_bytes()
        r = self.client.post("/menu-items", json=ITEM, headers=self.headers(self.viewer))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.data.read_bytes(), before)

    def test_staff_write_is_saved_and_can_be_read_back(self):
        before = len(self.client.get("/menu-items").json())
        r = self.client.post("/menu-items", json=ITEM, headers=self.headers(self.staff))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get(r.headers["location"]).json(), r.json())
        self.assertEqual(len(self.client.get("/menu-items").json()), before + 1)
        with TestClient(create_app(self.data, TokenRegistry())) as restarted:
            self.assertEqual(restarted.get(r.headers["location"]).json(), r.json())
            self.assertEqual(restarted.get("/whoami", headers=self.headers(self.staff)).status_code, 401)

    def test_expired_staff_token_cannot_write(self):
        self.now += 4 * 60 * 60
        before = self.data.read_bytes()
        self.assertEqual(self.client.post("/menu-items", json=ITEM,
                         headers=self.headers(self.staff)).status_code, 401)
        self.assertEqual(self.data.read_bytes(), before)

    def test_client_supplied_permission_cannot_grant_access(self):
        before = self.data.read_bytes()
        r = self.client.post("/menu-items", json={**ITEM, "permissions": ["menu:write"]},
                             headers={**self.headers(self.viewer), "X-Role": "staff"})
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.data.read_bytes(), before)

    def test_invalid_staff_input_does_not_write(self):
        before = self.data.read_bytes()
        self.assertEqual(self.client.post("/menu-items", json={**ITEM, "price": -1.0},
                         headers=self.headers(self.staff)).status_code, 422)
        self.assertEqual(self.data.read_bytes(), before)

    def test_original_unprotected_write_routes_are_not_exposed(self):
        before = self.data.read_bytes()
        for method, path in [("put", "/menu-items/1"), ("delete", "/menu-items/1"), ("post", "/orders")]:
            self.assertIn(self.client.request(method, path, json=ITEM).status_code, (404, 405))
        self.assertEqual(self.data.read_bytes(), before)

    def test_credentials_are_not_served(self):
        for path in ["/.classroom/security-credentials.json", "/data/menu.json", "/auth.py"]:
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertNotIn(self.staff, self.client.get("/openapi.json").text)


if __name__ == "__main__":
    unittest.main()
