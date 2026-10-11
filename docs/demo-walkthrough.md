# Bar API demonstration

Start the solution and open `/docs`. Use fresh data for the IDs below; otherwise use the ID returned when you create the order.

| Step | Request | Expected result | Discussion |
| --- | --- | --- | --- |
| 1 | GET /menu-items/1 | 200, one menu item | Which parts of this response does the contract describe? |
| 2 | POST /orders: table 3, item 1, quantity 2 | 201, new pending order; ID 12 on fresh data | What does the server assign? Follow the Location header. |
| 3 | GET /orders/12 | 200, stored order | Where did the response data come from? |
| 4 | PUT /orders/12: table 3, item 1, quantity 3 | 200, updated order | Why do we resend both table and items? |
| 5 | PUT /orders/11 with the same input | 409, ready order cannot change | The JSON is valid. Which business rule rejects it? |
| 6 | POST /orders with quantity 0 | 422 | Which constraint belongs to input validation? |
| 7 | POST /orders with menu_item_id 3 and quantity 1 | 422, item unavailable | The ID has the right type. Why is that insufficient? |
| 8 | Stop and restart, then GET /orders/12 | 200, quantity still 3 | How does persistence differ from an in-memory variable? |
| 9 | DELETE /orders/12 | 204, empty body | Which parts of CRUD have we now used? |
| 10 | GET /orders/12 | 404 | What should a client do with an expected failure? |

For steps 4 and 5 use:

```json
{"table": 3, "items": [{"menu_item_id": 1, "quantity": 3}]}
```

Trace one request through **API boundary -> service -> storage**, then inspect the response. Compare what Swagger documents with what the tests check. For the coding activity, use the [starter](../starter/README.md) and complete only its marked handler.

The Postman collection automates the request setup, not the business decisions. Its ID 12 examples assume fresh data; update them if you have already created other orders.
