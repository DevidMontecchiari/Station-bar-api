# 3. Locate validation and business rules

[← Previous: implement the endpoint](02-create-order.md) | [Learning path](../README.md#start-here) | [Next class: persistence →](04-persistence.md)

**Goal:** explain why a request succeeds or fails and locate the responsible code. Use your completed starter for the POST examples. Use the complete reference on port 8000 for the PUT example; update/delete routes are outside the starter.

Predict each result, try it, and inspect [models.py](../solution/bar_api/models.py), [service.py](../solution/bar_api/service.py) and [api.py](../solution/bar_api/api.py).

| Request | Expected result | Explanation to check |
| --- | --- | --- |
| POST order: table 3, item 1, quantity 2 | 201 | Input is valid and item is available |
| POST order: quantity 0 | 422 | Input-model constraint |
| POST order: item 3, quantity 1 | 422 | Service rejects an unavailable item |
| PUT /orders/11 with table 3, item 1, quantity 2 (**reference only**) | 409 | Service protects an already-ready order |

**Check:** explain why two different checks produce 422. Inspect the orders after rejected requests: no new order should have been created. Find where the service's error becomes an HTTP response.

**Transfer:** write one valid example and one meaningful failure for your project's operation. Name the layer responsible for each check.

---

[← Previous: implement the endpoint](02-create-order.md) | [Learning path](../README.md#start-here) | [Next class: persistence →](04-persistence.md)
