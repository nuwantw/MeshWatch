# Research: Tools and Frameworks for Building and Testing the MeshWatch API

- **Issue:** #23
- **Author:** @aliraza1628-del
- **Sprint:** Sprint 1
- **Status:** Ready for team review

## 1. Goal

MeshWatch needs a backend API that receives data from (simulated) IoT devices, stores it and serves it to the dashboard. This document compares the Python options for building that API, explains the server that runs it, and lists the tools we can use to test it. The result feeds ADR-0006.

## 2. Requirements from the MeshWatch context

| # | Requirement | Why it matters for MeshWatch |
|---|-------------|------------------------------|
| R1 | Handle many small, concurrent requests | Several devices/peers report status at the same time |
| R2 | Validate incoming device data | Simulated or faulty devices can send bad payloads |
| R3 | Push live updates to the dashboard | Dashboard should update without manual reload (WebSockets) |
| R4 | Auto-generated API documentation | Six developers work on the same API in parallel |
| R5 | Easy to test automatically | Every PR goes through review per ADR-0001 |
| R6 | Low learning curve | Short sprint, mixed experience in the team |

## 3. Framework comparison: FastAPI vs Flask

| Criterion | FastAPI | Flask |
|-----------|---------|-------|
| Interface standard | ASGI (asynchronous) | WSGI (synchronous by design) |
| Concurrency (R1) | Native async/await; one process handles many waiting connections | Scales by adding threads/processes |
| Data validation (R2) | Built in via Pydantic; invalid payloads rejected with HTTP 422 | Manual or extra libraries (e.g. Marshmallow) |
| WebSockets (R3) | Built in | Needs an extension (e.g. Flask-SocketIO) |
| API docs (R4) | OpenAPI + Swagger UI at /docs generated automatically | Needs an extension (e.g. Flasgger) |
| Testing (R5) | TestClient included | Test client included |
| Learning curve (R6) | Small, needs type hints and async basics | Very small, many tutorials |
| Maturity | Younger, very popular for APIs | Very mature, huge ecosystem |

**Assessment.** Flask is simpler and very mature, but most features MeshWatch needs (validation, WebSockets, API docs, async I/O) would come from add-ons. FastAPI ships them built in and is designed for JSON APIs with many concurrent clients.

## 4. Uvicorn: the ASGI server

FastAPI is only the framework. It needs an ASGI server to listen on a port and handle connections. Uvicorn is the standard choice:

- Lightweight, fast ASGI server (`uvicorn[standard]` adds uvloop and httptools).
- Supports HTTP and WebSockets (needed for R3).
- Auto-reload for development: `uvicorn src.api.main:app --reload`
- Multiple worker processes for more load: `--workers 4`
- Runs well in Docker.

Alternatives: Hypercorn (ASGI, HTTP/2), Gunicorn (process manager with Uvicorn workers). For our scope, plain Uvicorn is enough.

## 5. Testing tools

| Tool | Purpose | Use in MeshWatch |
|------|---------|------------------|
| pytest | Test runner | Main test framework |
| FastAPI TestClient (httpx) | Call endpoints without starting a server | Endpoint tests |
| httpx AsyncClient + pytest-asyncio | Test async code paths | Async ingestion tests |
| pytest-cov | Code coverage | Coverage in PRs |
| Ruff | Linting and formatting | Consistent style in reviews |
| Schemathesis | Tests generated from the OpenAPI schema | Edge cases in device payloads |
| Locust | Load testing | Simulate many devices at once |
| GitHub Actions | CI | Run tests on every PR |

## 6. Proof of concept in this branch

- `src/api/main.py`: minimal FastAPI app with `/health`, `POST /devices/status`, `GET /devices/status`
- `src/api/tests/test_main.py`: 3 tests (health, report + list, invalid payload → 422)

Run from the repo root:

```bash
pip install -r requirements.txt
python -m pytest
uvicorn src.api.main:app --reload   # docs at http://127.0.0.1:8000/docs
```

## 7. Recommendation

Use **FastAPI** + **Uvicorn**, with **pytest + TestClient** as the baseline testing stack. Locust and Schemathesis are optional for later sprints. The decision is proposed in ADR-0006.

## 8. Open questions for the team

1. Do devices talk to the API over HTTP, or do we add MQTT later?
2. Which storage do we use (affects async vs sync database driver)?
3. Do we set up GitHub Actions CI this sprint or put it in the Product Backlog?
