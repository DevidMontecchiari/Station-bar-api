"""Login -> user menu -> admin area, using the same business service as the API."""
from pathlib import Path
import secrets
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from bar_api.models import MenuItemInput
from bar_api.service import BarError
from .accounts import AccountStore
from .auth import Principal
from .sessions import LoginAttempts, SessionStore

COOKIE = "station_bar_session"
HERE = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=HERE / "templates")


def browser_user(request: Request) -> Principal:
    session = request.app.state.sessions.get(request.cookies.get(COOKIE))
    user = request.app.state.accounts.principal(session.username) if session and session.username else None
    if user is None:
        raise HTTPException(303, headers={"Location": "/login"})
    return user


BrowserUser = Annotated[Principal, Depends(browser_user)]


def can_manage_menu(user: BrowserUser):
    # Hiding a button is only presentation. This dependency protects GET and POST.
    if "menu:write" not in user.permissions:
        raise HTTPException(403, detail="Your account cannot manage the menu.")
    return user


MenuAdmin = Annotated[Principal, Depends(can_manage_menu)]


def check_csrf(request, value):
    session = request.app.state.sessions.get(request.cookies.get(COOKIE))
    if not session or not secrets.compare_digest(session.csrf, value):
        raise HTTPException(403, detail="Form expired or could not be verified. Reload and retry.")


def install_pages(app, accounts: AccountStore, secure_cookies=False):
    app.state.accounts = accounts
    app.state.sessions = SessionStore()
    app.state.login_attempts = LoginAttempts()
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="security-static")
    router = APIRouter(include_in_schema=False)

    def render(request, name, user=None, status=200, **context):
        session = app.state.sessions.get(request.cookies.get(COOKIE))
        role = accounts.accounts[user.username].role if user else None
        return templates.TemplateResponse(request=request, name=name,
            context={"user": user, "role": role, "csrf": session.csrf if session else "", **context},
            status_code=status)

    def set_session(response, token, age):
        response.set_cookie(COOKIE, token, max_age=age, httponly=True,
                            secure=secure_cookies, samesite="lax", path="/")

    @app.middleware("http")
    async def response_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'none'; style-src 'self'; img-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
        ) if request.url.path not in ("/docs", "/redoc", "/docs/oauth2-redirect") else "frame-ancestors 'none'"
        return response

    @router.get("/")
    def home():
        return RedirectResponse("/menu", status_code=303)

    @router.get("/login")
    def login_page(request: Request):
        session = app.state.sessions.get(request.cookies.get(COOKIE))
        if session and session.username:
            return RedirectResponse("/menu", status_code=303)
        token, session = app.state.sessions.issue()
        app.state.sessions.revoke(request.cookies.get(COOKIE))
        response = render(request, "login.html", csrf=session.csrf)
        set_session(response, token, 600)
        return response

    @router.post("/login")
    def login(request: Request, username: Annotated[str, Form(max_length=64)],
              password: Annotated[str, Form(max_length=256)], csrf: Annotated[str, Form()] = ""):
        check_csrf(request, csrf)
        if app.state.login_attempts.blocked(username):
            return render(request, "login.html", status=429, error="Too many attempts. Please wait one minute.")
        account = accounts.authenticate(username, password)
        if account is None:
            app.state.login_attempts.failure(username)
            return render(request, "login.html", status=401, error="Username or password not recognised.")
        app.state.login_attempts.clear(username)
        app.state.sessions.revoke(request.cookies.get(COOKIE))
        token, _ = app.state.sessions.issue(account.username)
        response = RedirectResponse("/menu", status_code=303)
        set_session(response, token, 3600)
        return response

    @router.post("/logout")
    def logout(request: Request, user: BrowserUser, csrf: Annotated[str, Form()] = ""):
        check_csrf(request, csrf)
        app.state.sessions.revoke(request.cookies.get(COOKIE))
        response = RedirectResponse("/login", status_code=303)
        response.delete_cookie(COOKIE, path="/", secure=secure_cookies, httponly=True, samesite="lax")
        return response

    @router.get("/menu")
    def user_menu(request: Request, user: BrowserUser):
        return render(request, "menu.html", user, items=app.state.service.list_records("menu_items"))

    @router.get("/admin")
    def admin(request: Request, user: MenuAdmin):
        return render(request, "admin.html", user, assignments=accounts.assignments(), saved=request.query_params.get("saved") == "1")

    @router.post("/admin/menu-items")
    def add_menu_item(request: Request, user: MenuAdmin, name: Annotated[str, Form(max_length=120)],
                      price: Annotated[str, Form(max_length=20)], csrf: Annotated[str, Form()] = ""):
        check_csrf(request, csrf)
        try:
            # HTML fields arrive as strings; preserve the service's strict model.
            item = MenuItemInput(name=name, price=float(price), currency="CHF", available=True)
            app.state.service.create_menu_item(item.model_dump())
        except (ValueError, ValidationError, BarError):
            return render(request, "admin.html", user, status=422, assignments=accounts.assignments(),
                          error="Enter a name and a valid non-negative price.")
        return RedirectResponse("/admin?saved=1", status_code=303)

    # Friendly HTML for page denials; API errors keep JSON and HTTP semantics.
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from fastapi.exception_handlers import http_exception_handler
    @app.exception_handler(StarletteHTTPException)
    async def page_error(request, error):
        if error.status_code == 403 and request.url.path in ("/admin", "/admin/menu-items", "/login", "/logout"):
            return render(request, "denied.html", status=403, error=error.detail)
        return await http_exception_handler(request, error)

    app.include_router(router)
