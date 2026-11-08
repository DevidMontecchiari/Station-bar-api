# 5. From a prototype to a connected interface

[Learning path](../README.md) -> [Previous: persistence](04-persistence.md)

**Exercise 5** is a reference for choosing and inspecting an interface route for your project. In class, we compare selected examples and discuss your choices and questions. The [setup](#setup) and [optional extension](#your-turn) remain available for independent follow-up; there is no timed coding activity to complete during the lecture.

## Setup

Fork or safely update Station Bar, then run `python start_class.py` from its root. It prepares the environments and starts the examples; open a labelled port from the printed list. See [Class startup and SQLite inspection](../docs/class-start.md) for the exact workflow. The [individual commands](../extensions/frontend/README.md#1-update-and-prepare-once) remain an alternative; do not start a second copy of the same server.

Use these instructions when you want to run the examples yourself. The lecturer uses prepared examples for the classroom comparison.

## Lecturer demo

We will use selected examples to compare the routes, according to the questions in class:

1. Observe the browser-only prototype and explain what reload loses.
2. Inspect the API-client request and read back the saved order.
3. Compare Jinja2 HTML rendering with the JSON/DOM route.

Use the [inspection walkthrough](../extensions/frontend/README.md#3-observe-inspect-then-stop) to revisit the demonstration afterwards.

## Your turn

**Optional independent follow-up.** Start from one user interaction your project needs. Inspect one supplied example or a relevant optional walkthrough: where is the HTML built, which request reaches the API, and what is saved? The static version is a layout prototype; the connected examples show the backend integration.

If useful for your project or practice, try **one** small extension in a branch: a menu filter or order lookup. Follow the [extension guidance](../extensions/frontend/README.md#4-extend-one-small-part). Explain the changed code and verify the feature plus an order success and rejection. This is not an additional required task or submission.

Use the comparison to decide your next project step and identify questions for coaching. Completing all three variants is not required.

**For coaching:** update your existing project README with the current workflow, setup and questions. Follow Moodle for the full preparation instructions, submission deadline and your Teams slot. Keep your project choices and existing assessment requirements.
