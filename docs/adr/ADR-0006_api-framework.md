# ADR-0006: Use FastAPI and Uvicorn for the MeshWatch API

- **Status:** Proposed
- **Date:** 2026-11-20
- **Related issue:** #23
- **Research:** `docs/research/fastapi-uvicorn-research.md`

## Context

MeshWatch needs an HTTP API that receives status data from (simulated) IoT devices, validates it and provides it to the HTML dashboard, ideally with live updates. Many devices may report concurrently. Six developers work on the API in parallel, so the API contract must be clear and every change must be testable in a PR.

No existing ADR defines the backend framework or how the API is served and tested.

## Options considered

1. **FastAPI + Uvicorn:** async ASGI framework with built-in validation (Pydantic), WebSockets and OpenAPI docs.
2. **Flask + Gunicorn:** mature, simple WSGI framework; validation, WebSockets and API docs need extensions.

## Decision

We use **FastAPI** as the API framework, run by the **Uvicorn** ASGI server. Tests use **pytest** with FastAPI's **TestClient**.

## Consequences

**Positive**
- Device payloads are validated automatically; invalid data is rejected with HTTP 422.
- Swagger UI at `/docs` documents the API for the whole team without extra work.
- Native async and WebSocket support fit concurrent devices and a live dashboard.
- Endpoints can be tested without starting a server, which keeps PR checks fast.

**Negative**
- Team members must learn type hints, Pydantic and basic `async`/`await`.
