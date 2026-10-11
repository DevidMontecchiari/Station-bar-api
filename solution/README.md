# Complete reference API

In the Codespace terminal run `python run.py solution --host 0.0.0.0` from the repository root. Open port8000 in the Ports panel, then add /docs.

The reference supports menu/order CRUD. Only pending orders can be changed or deleted; referenced menu items cannot be deleted. ID and status are assigned by the server. Errors contain code and message. Order status transitions are a later extension.

Follow the [contract activity](../exercises/01-api-contract.md), [code map](../docs/code-map.md) and [demonstration walkthrough](../docs/demo-walkthrough.md).

Run `python check.py solution --full` for the full reference behaviour checks. requirements.txt pins runtime dependencies; requirements-test.txt adds checks; requirements-lock.txt records the original Windows test environment.

[Setup and learning path](../README.md)
