"""JWT outcomes with temporary data; run start_security.py --jwt --check."""
import base64
import json
from pathlib import Path
import tempfile
import time
import unittest
import jwt
from fastapi.testclient import TestClient
from extensions.security.accounts import Account, AccountStore, password_hash
from extensions.security.app import create_app
from extensions.security.auth import TokenRegistry
from extensions.security.jwt_api import AUDIENCE, ISSUER, JWTService, TOKEN_SECONDS

ITEM = {"name": "JWT workshop tea", "price": 4.0, "currency": "CHF", "available": True}


class JWTChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hash = password_hash.hash("fictional-test-password")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "menu.json"
        self.accounts = AccountStore([Account(name, name, self.hash) for name in ["user", "admin"]])
        self.opaque = TokenRegistry()
        self.jwt = JWTService()
        self.app = create_app(self.data, self.opaque, self.accounts, jwt_service=self.jwt)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def token(self, username):
        r = self.client.post("/jwt/token", json={"username": username, "password": "fictional-test-password"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers["cache-control"], "no-store")
        self.assertEqual(r.json()["expires_in"], TOKEN_SECONDS)
        return r.json()["access_token"]

    def headers(self, token):
        return {"Authorization": "Bearer " + token}

    def mint(self, updates=None, missing=None, algorithm="HS256", typ="at+jwt"):
        """Mint controlled invalid cases using this test's private issuer key."""
        now = int(time.time())
        claims = {"iss": ISSUER, "aud": AUDIENCE, "sub": "admin", "iat": now,
                  "nbf": now, "exp": now + 300, "scope": "menu:write"}
        claims.update(updates or {})
        if missing:
            claims.pop(missing)
        key = self.jwt.key if algorithm != "HS384" else self.jwt.key * 2
        return jwt.encode(claims, key if algorithm != "none" else "",
                          algorithm=algorithm, headers={"typ": typ})

    def denied(self, token, status=401):
        before = self.data.read_bytes()
        r = self.client.post("/jwt/menu-items", json=ITEM, headers=self.headers(token))
        self.assertEqual(r.status_code, status)
        self.assertEqual(self.data.read_bytes(), before)

    def test_user_identity_is_valid_but_write_is_denied(self):
        token = self.token("user")
        self.assertEqual(self.client.get("/jwt/whoami", headers=self.headers(token)).json(),
                         {"username": "user", "permissions": []})
        self.denied(token, 403)

    def test_admin_write_persists_but_restart_invalidates_token(self):
        token = self.token("admin")
        r = self.client.post("/jwt/menu-items", json=ITEM, headers=self.headers(token))
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get(r.headers["location"]).json(), r.json())
        with TestClient(create_app(self.data, TokenRegistry(), self.accounts, jwt_service=JWTService())) as restarted:
            self.assertEqual(restarted.get(r.headers["location"]).json(), r.json())
            self.assertEqual(restarted.get("/jwt/whoami", headers=self.headers(token)).status_code, 401)

    def test_missing_malformed_wrong_scheme_rejected(self):
        before = self.data.read_bytes()
        for headers in [{}, {"Authorization": "Basic abc"}, self.headers("not.jwt"), self.headers("")]:
            r = self.client.post("/jwt/menu-items", json=ITEM, headers=headers)
            self.assertEqual(r.status_code, 401)
            self.assertEqual(r.headers["www-authenticate"], "Bearer")
            self.assertEqual(self.data.read_bytes(), before)

    def test_bad_password_unknown_user_and_client_role_rejected(self):
        for name in ["user", "unknown"]:
            r = self.client.post("/jwt/token", json={"username": name, "password": "wrong"})
            self.assertEqual(r.status_code, 401)
            self.assertEqual(r.json(), {"detail": "Username or password not recognised."})
        self.assertEqual(self.client.post("/jwt/token", json={"username": "user", "password": "fictional-test-password", "role": "admin"}).status_code, 422)

    def test_failed_attempts_are_limited(self):
        for _ in range(5):
            self.client.post("/jwt/token", json={"username": "user", "password": "wrong"})
        self.assertEqual(self.client.post("/jwt/token", json={"username": "user", "password": "wrong"}).status_code, 429)

    def test_expired_and_future_times_rejected(self):
        now = int(time.time())
        for changes in [{"exp": now - 1}, {"nbf": now + 300}, {"iat": now + 300}]:
            self.denied(self.mint(changes))

    def test_wrong_issuer_audience_algorithm_and_type_rejected(self):
        for changes in [{"iss": "another-issuer"}, {"aud": "another-api"}, {"aud": [AUDIENCE]}, {"sub": "unknown"}]:
            self.denied(self.mint(changes))
        for algorithm in ["HS384", "none"]:
            self.denied(self.mint(algorithm=algorithm))
        self.denied(self.mint(typ="JWT"))

    def test_required_and_typed_claims(self):
        for name in ["iss", "aud", "sub", "iat", "nbf", "exp", "scope"]:
            self.denied(self.mint(missing=name))
        for changes in [{"sub": ""}, {"scope": ["menu:write"]}, {"exp": str(int(time.time()) + 300)}]:
            self.denied(self.mint(changes))

    def test_payload_edit_does_not_grant_admin(self):
        header, body, signature = self.token("user").split(".")
        claims = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        claims.update(sub="admin", scope="menu:write")
        changed = base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
        self.denied(".".join([header, changed, signature]))

    def test_scope_bounded_by_current_account_permissions(self):
        self.denied(self.mint({"sub": "user"}), 403)
        self.denied(self.mint({"scope": ""}), 403)
        token = self.token("admin")
        self.accounts.accounts["admin"] = Account("admin", "user", self.hash)
        self.denied(token, 403)
        del self.accounts.accounts["admin"]
        self.denied(token)

    def test_opaque_and_jwt_tokens_not_interchangeable(self):
        opaque, _ = self.opaque.issue(self.accounts.principal("admin"))
        self.denied(opaque)
        self.assertEqual(self.client.get("/whoami", headers=self.headers(self.token("admin"))).status_code, 401)

    def test_claims_are_limited_and_no_browser_session_issued(self):
        token = self.token("admin")
        self.assertEqual(set(self.jwt.verify(token)), {"iss", "aud", "sub", "iat", "nbf", "exp", "scope"})
        self.assertEqual(self.client.get("/admin", follow_redirects=False).status_code, 303)
        self.assertNotIn("station_bar_session", self.client.cookies)

    def test_openapi_schemes_and_default_mode(self):
        paths = self.client.get("/openapi.json").json()["paths"]
        self.assertEqual(paths["/jwt/menu-items"]["post"]["security"], [{"JWT access token (optional)": []}])
        self.assertNotIn("security", paths["/jwt/token"]["post"])
        with TestClient(create_app(self.data, TokenRegistry(), self.accounts)) as baseline:
            self.assertEqual(baseline.post("/jwt/token", json={}).status_code, 404)
            self.assertEqual(baseline.get("/login").status_code, 200)

    def test_admin_invalid_input_leaves_data_unchanged(self):
        before = self.data.read_bytes()
        r = self.client.post("/jwt/menu-items", json={**ITEM, "price": -1.0}, headers=self.headers(self.token("admin")))
        self.assertEqual(r.status_code, 422)
        self.assertEqual(self.data.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
