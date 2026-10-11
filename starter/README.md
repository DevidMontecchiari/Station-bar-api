# Create an order

Start from the repository root with `python run.py starter`; see the [setup instructions](../README.md#run). Valid `POST /orders` requests currently return `501`. Other routes are provided.

1. Inspect `GET /menu-items/1` and the `POST /orders` request schema in `/docs`.
2. Open `bar_api/api.py` and find `BEGIN CREATE ORDER EXERCISE`.
3. Pass `body.model_dump()` to `service.create_order`, set the `Location` response header to the created order's URL and return the order. The route already declares status `201`.
4. Send an order for table 3 with item 1, quantity 2. Then try quantity 0 and unavailable item 3. Compare the responses and identify the layer responsible for each result.
5. After trying it, compare your handler with `../solution/bar_api/api.py`.

This activity changes one HTTP handler. The input models, business logic and persistence are supplied. The [walkthrough](../docs/demo-walkthrough.md) contains additional requests for the completed version.
