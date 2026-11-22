# Optional JWT practice: the same action, a signed credential

[Exercise 6](../../exercises/06-security.md) · [Browser login walkthrough](add-login-to-your-project.md) · [Setup](../../extensions/security/README.md)

Use this route if your API client will present a signed access token. The browser-session route remains available. Both use the same trusted accounts, `menu:write` permission and saved menu. Follow **08A, A23–A26** alongside this guide. Choose an appropriate implementation for your project; completing every route is not required.

## 1. Start and obtain a token

1. Update your repository, preserving local edits. If the security example already occupies port 8003, stop it with **Ctrl+C in its own terminal**.
2. From the repository root run:

   ```shell
   python start_security.py --jwt
   ```

   The launcher installs the optional PyJWT dependency in `.venv-security` and uses that environment's Python. Keep the terminal open. In Codespaces, keep **8003 Private** and open its forwarded HTTPS URL ending in **`/docs`**. VS Code also has the task **Station Bar: JWT practice**. This starts the same service with additional routes; it does not require another port.
3. Open `.classroom/security-credentials.json` **locally**. Use your own generated `user` and `admin` **passwords**, not the separate opaque `token` values. This file appears after the first startup.
4. In **Optional JWT exercise → POST `/jwt/token` → Try it out**, enter:

   ```json
   {"username": "user", "password": "replace with your local user password"}
   ```

5. Execute. Copy only the returned **`access_token`** value. Its lifetime is **300 seconds**.
6. Open **Authorize → JWT access token (optional)**, paste that value and authorise. Do not add `Bearer ` yourself. This field is separate from the older opaque-token comparison. Swagger adds the bearer header to requests using this scheme.

Do not share passwords/tokens in Moodle, screenshots, commits or external token-decoder websites. A signed JWT payload is readable; it is not encrypted.

You can also [register a fictional account](../../extensions/security/README.md#create-an-account) at `/signup` and use its lowercase username and chosen password at `/jwt/token`. That password is not on the seeded teaching access sheet. The new account receives the user role, with no `menu:write` permission.

## 2. Run the same operation with two identities

Use **GET `/jwt/whoami`** first: the user has no `menu:write` permission. Then try **POST `/jwt/menu-items`** with:

```json
{"name": "JWT workshop tea", "price": 4.0, "currency": "CHF", "available": true}
```

| Credential for the JWT routes | Expected result | What this proves |
| --- | --- | --- |
| No token, invalid token or expired token | **401** | A valid credential is required. |
| Valid `user` JWT | **403** on POST | Authentication alone does not grant permission. |
| Valid `admin` JWT | **201** on POST | The permitted action reaches the service. |

For the admin attempt, **Logout** from the JWT authorisation field, obtain a new token from `/jwt/token` with your local admin password, and authorise again. Do not edit a token's username or scope to switch roles: that breaks its signature.

Inspect **`extensions/security/data/menu.json`**. A rejected write changes nothing. For a successful write, use the returned ID with public **GET `/menu-items/{id}`** or revisit `/menu` after browser sign-in. Browser sessions and JWT authorisation are independent: obtaining a JWT does not log you into `/admin`.

## 3. Trace the functions

```text
POST /jwt/token
  AccountStore.authenticate() -> password hash verified
  JWTService.issue()           -> signed claims + five-minute expiry

POST /jwt/menu-items + Authorization: Bearer <JWT>
  JWTService.verify()          -> signature + trusted issuer/audience + time checks
  jwt_user()                  -> current account + permitted token scope
  jwt_staff()                 -> require menu:write
  BarService.create_menu_item() -> existing validation/storage
```

The route and JWT functions are in [`extensions/security/jwt_api.py`](../../extensions/security/jwt_api.py). The dependency chain keeps credential checking separate from the business action.

The verification call fixes the algorithm and expected issuer/audience **on the server**:

```python
claims = jwt.decode(token, self.key, algorithms=[ALGORITHM],
                    issuer=ISSUER, audience=AUDIENCE,
                    options={"require": ["iss", "aud", "sub", "iat", "nbf", "exp", "scope"],
                             "strict_aud": True})
```

The complete function also checks the token type and claim types. `sub` identifies the local account, `aud` identifies this API, and `exp` limits lifetime. `scope` is a server-issued permission snapshot. The effective permissions are its **intersection with the account's current permissions**. Removing a permission from the trusted policy therefore blocks the next write even if the token has not expired. Adding a permission requires a new token if it was not in the previous scope. Accounts are still looked up: this example is not a completely stateless application.

## 4. Verify and adapt one action

Run the existing login/API tests and the JWT tests together:

```shell
python start_security.py --jwt --check
```

These use temporary fictional data. JWT checks cover successful/denied writes, tampering, expiry, wrong issuer/audience/algorithm, missing claims, changed account permissions and restart. You can also wait five minutes and repeat `/jwt/whoami`: expect 401, then obtain a fresh token.

For your project:

1. Keep your existing account lookup, business service and JSON/database storage. Map verified identities to your trusted account records.
2. Choose one meaningful protected operation. Adapt `JWTUser`/`JWTStaff` and the permission name to that policy; apply it to every route that can perform the operation.
3. Keep token validation before the permission check. Never accept an admin role supplied with the login request or trust a decoded-but-unverified payload.
4. Reproduce one allowed operation and one denied operation, checking stored data. In your existing README, explain the chosen route, where permission is enforced, how you verified it and what remains limited.

The quality of the explanation, implementation and checks matters. JWT is an optional technique, not a separate bonus or a new mandatory deliverable. Full assessment requirements remain in Moodle.

## Boundaries to understand

- **Local credential exchange, not delegated OAuth:** `/jwt/token` accepts JSON credentials for our own app. It is not a standards-compliant OAuth token endpoint or an OpenID Connect provider. For external sign-in, use the separate [Auth0/Keycloak routes](add-login-to-your-project.md#login-options).
- **Single-process teaching key:** HS256 uses a fresh random 256-bit key held only in this server process. Restart invalidates earlier JWTs while passwords and menu data remain. Production or multiple-service deployments need an explicit key-storage, distribution and rotation design.
- **Logout differs:** browser logout revokes its session; it does not revoke a JWT. Swagger Logout stops sending a saved token but does not invalidate copies. This sample relies on expiry, current account policy and the process key; it has no per-token revocation or refresh-token flow.
- **Transport matters:** use the private HTTPS Codespaces URL. The loopback HTTP example is for local development. The sample does not prescribe browser token storage or automatically secure previous app variants.

## Official references

- [FastAPI: password hashing and JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) — compare the functions and dependency approach. Its OAuth2 form-based example differs from our deliberately labelled JSON exchange.
- [PyJWT API](https://pyjwt.readthedocs.io/en/stable/api.html) — encoding, decoding, fixed algorithms and required claims.
- [RFC 8725: JWT best current practices](https://www.rfc-editor.org/rfc/rfc8725.html) — validation and token-substitution concerns.
