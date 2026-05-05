---
created: 2026-04-19T05:29:03 (UTC +03:00)
tags: []
source: https://fastapi.tiangolo.com/tutorial/
author: 
---

# Tutorial - User Guide - FastAPI

> ## Excerpt
> FastAPI framework, high performance, easy to learn, fast to code, ready for production

---
This tutorial shows you how to use **FastAPI** with most of its features, step by step.

Each section gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly to any specific one to solve your specific API needs.

It is also built to work as a future reference so you can come back and see exactly what you need.

## Run the code[¶](https://fastapi.tiangolo.com/tutorial/#run-the-code)

All the code blocks can be copied and used directly (they are actually tested Python files).

To run any of the examples, copy the code to a file `main.py`, and start `fastapi dev`:

```
fast →fastapi dev   FastAPI   Starting development server 🚀             Searching for package file structure from directories             with __init__.py files             Importing from /home/user/code/awesomeapp    module   🐍 main.py      code   Importing the FastAPI app object from the module with             the following code:from main import app       app   Using import string: main:app    server   Server started at http://127.0.0.1:8000    server   Documentation at http://127.0.0.1:8000/docs       tip   Running in development mode, for production use:             fastapi run             Logs:      INFO   Will watch for changes in these directories:             ['/home/user/code/awesomeapp']      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C             to quit)      INFO   Started reloader process [383138] using WatchFiles      INFO   Started server process [383153]      INFO   Waiting for application startup.      INFO   Application startup complete.restart ↻
```

It is **HIGHLY encouraged** that you write or copy the code, edit it and run it locally.

Using it in your editor is what really shows you the benefits of FastAPI, seeing how little code you have to write, all the type checks, autocompletion, etc.

___

## Install FastAPI[¶](https://fastapi.tiangolo.com/tutorial/#install-fastapi)

The first step is to install FastAPI.

Make sure you create a [virtual environment](https://fastapi.tiangolo.com/virtual-environments/), activate it, and then **install FastAPI**:

```
fast →pip install "fastapi[standard]"████████████████████████████████████████ 100%restart ↻
```

Note

When you install with `pip install "fastapi[standard]"` it comes with some default optional standard dependencies, including `fastapi-cloud-cli`, which allows you to deploy to [FastAPI Cloud](https://fastapicloud.com/).

If you don't want to have those optional dependencies, you can instead install `pip install fastapi`.

If you want to install the standard dependencies but without the `fastapi-cloud-cli`, you can install with `pip install "fastapi[standard-no-fastapi-cloud-cli]"`.

Tip

FastAPI has an [official extension for VS Code](https://marketplace.visualstudio.com/items?itemName=FastAPILabs.fastapi-vscode) (and Cursor), which provides a lot of features, including a path operation explorer, path operation search, CodeLens navigation in tests (jump to definition from tests), and FastAPI Cloud deployment and logs, all from your editor.

## Advanced User Guide[¶](https://fastapi.tiangolo.com/tutorial/#advanced-user-guide)

There is also an **Advanced User Guide** that you can read later after this **Tutorial - User guide**.

The **Advanced User Guide** builds on this one, uses the same concepts, and teaches you some extra features.

But you should first read the **Tutorial - User Guide** (what you are reading right now).

It's designed so that you can build a complete application with just the **Tutorial - User Guide**, and then extend it in different ways, depending on your needs, using some of the additional ideas from the **Advanced User Guide**.
