"""Three presentation adapters. Only the existing API owns business rules/storage.

The browser fetch example uses a same-origin proxy for Codespaces convenience.
The Jinja example calls the same API on the server, then renders HTML.
Neither adapter opens the backend's JSON file.
"""
from pathlib import Path
from typing import Annotated
import httpx
from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

HERE = Path(__file__).resolve().parent


def api_call(base, method, path, payload=None):
    """Bounded timeout, no retries of writes, and a useful failure for the interface."""
    try:
        response = httpx.request(method, base.rstrip('/') + path, json=payload,
                                 timeout=5, trust_env=False)
        try:
            data = response.json()
        except ValueError:
            return 502, {'message': 'The API did not return JSON.'}
        return response.status_code, data
    except httpx.RequestError:
        return 503, {'message': 'The API is unavailable. Start the JSON solution on port 8000. '
                    'If an order was being submitted, check saved orders before retrying.'}


def create_app(variant, api_url='http://127.0.0.1:8000'):
    if variant not in {'static', 'api-client', 'server-rendered'}:
        raise ValueError('Unknown frontend variant')
    app = FastAPI(title=f'Station Bar: {variant}', docs_url=None, redoc_url=None)
    app.mount('/shared', StaticFiles(directory=HERE / 'shared'), name='shared')
    if variant in {'static', 'api-client'}:
        folder = HERE / variant
        app.mount('/files', StaticFiles(directory=folder), name='files')

        @app.get('/')
        def home():
            return FileResponse(folder / 'index.html')

    if variant == 'api-client':
        # Explicit routes, not an arbitrary URL proxy. Same-origin browser /api/*
        # becomes a server-to-server call to the existing backend on port 8000.
        @app.get('/api/menu-items')
        def menu():
            status, data = api_call(api_url, 'GET', '/menu-items')
            return JSONResponse(data, status_code=status)

        @app.post('/api/orders')
        def create_order(payload: dict):
            status, data = api_call(api_url, 'POST', '/orders', payload)
            return JSONResponse(data, status_code=status)

        @app.get('/api/orders/{order_id}')
        def read_order(order_id: int):
            status, data = api_call(api_url, 'GET', f'/orders/{order_id}')
            return JSONResponse(data, status_code=status)

    if variant == 'server-rendered':
        templates = Jinja2Templates(directory=HERE / 'server-rendered' / 'templates')

        def page(request, *, error='', status=200, order=None, values=None):
            menu_status, menu_data = api_call(api_url, 'GET', '/menu-items')
            if menu_status != 200:
                error = error or menu_data.get('message', 'Menu unavailable.')
                status = menu_status
                menu_data = []
            return templates.TemplateResponse(request=request, name='index.html',
                context={'menu': menu_data, 'error': error, 'order': order,
                         'values': values or {'table': 3, 'quantity': 2, 'item': 1}},
                status_code=status)

        @app.get('/')
        def home(request: Request):
            return page(request)

        @app.post('/orders')
        def create_order(request: Request, table: Annotated[str, Form()],
                         item: Annotated[str, Form()], quantity: Annotated[str, Form()]):
            values = {'table': table, 'item': item, 'quantity': quantity}
            try:
                payload = {'table': int(table), 'items': [
                    {'menu_item_id': int(item), 'quantity': int(quantity)}]}
            except ValueError:
                return page(request, error='Enter whole numbers for table and quantity.',
                            status=422, values=values)
            status, data = api_call(api_url, 'POST', '/orders', payload)
            if status != 201:
                return page(request, error=data.get('message', 'Order not saved.'),
                            status=status, values=values)
            # Post/Redirect/Get: refreshing the result does not create another order.
            return RedirectResponse(f"/orders/{data['id']}", status_code=303)

        @app.get('/orders/{order_id}')
        def order_page(request: Request, order_id: int):
            status, data = api_call(api_url, 'GET', f'/orders/{order_id}')
            if status != 200:
                return page(request, error=data.get('message', 'Order not found.'), status=status)
            return page(request, order=data)

    return app
