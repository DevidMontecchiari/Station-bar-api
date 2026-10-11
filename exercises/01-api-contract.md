# 1. Explore an API contract

[← Learning path](../README.md#start-here) | **1. API contract** | [Next: code map →](../docs/code-map.md)

**Goal:** use documentation to predict and investigate an unfamiliar API. Use the complete reference on port 8000; no code changes are needed.

1. Open /docs. Identify the method and path for reading one menu item and creating an order.
2. Find the required fields and the quantity constraint for an order. Predict the response to the two requests below.
3. Execute both and compare status, response body and headers with your predictions.

Valid request:

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 2}]}
```

Change quantity to `0` for the second request.

**Check:** the valid request returns 201, an ID, pending status and Location. Quantity 0 returns 422. Retrieve the created order using its returned ID; do not assume the ID remains 12 after earlier runs.

**Transfer:** select one operation in your group project. What information would another developer need to call it and recognise success or failure?

---

[← Learning path](../README.md#start-here) | **1. API contract** | [Next: code map →](../docs/code-map.md)
