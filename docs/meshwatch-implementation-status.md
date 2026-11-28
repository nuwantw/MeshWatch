# MeshWatch Implementation Status

Audit date: 2026-11-28

## Feature status

| Feature | Status | Implementation |
|---|---|---|
| Sensor simulation | Implemented | [src/sensor_simulator.py](../src/sensor_simulator.py) generates unique JSON readings and can send them over HTTP. |
| mDNS peer discovery | Implemented with Docker fallback | [src/discovery.py](../src/discovery.py) uses zeroconf when available. Docker Compose uses static peer URLs because multicast can be blocked by container networking. |
| Gossip protocol | Implemented | `/gossip/readings` exchanges JSON readings and `/gossip/sync` pulls and pushes through configured peers. |
| Data storage | Implemented | [src/storage.py](../src/storage.py) atomically persists readings, statuses, and peers in JSON, with duplicate IDs deduplicated. |
| Web dashboard | Implemented | [frontend/index.html](../frontend/index.html) retains historical Chart.js charts and adds status, peer, sync, and alert views. |
| Alerting | Implemented | `/alerts` evaluates configurable high thresholds for temperature, humidity, and light. |
| Multiple node support | Implemented | Docker Compose runs three persistent simulated node services and three simulators. |
| Node status monitoring | Implemented | `/devices/status` stores reports and `/devices/status` marks stale reports unavailable after a timeout. |
| Configuration and setup | Implemented | Environment variables, Docker Compose, README setup instructions, and `/node` identity endpoint are provided. |

## Existing behavior preserved

The original `/health`, `POST /devices/status`, `GET /devices/status`, `POST /readings`, `GET /readings`, historical time filtering, sensor-type filtering, and dashboard chart remain available. Sensor readings now have an additive `reading_id` field.

## Reliability behavior

- A reading is accepted once per `reading_id`; repeated delivery is ignored.
- JSON is written through a temporary file and atomic replacement.
- Gossip failures are returned as peer errors instead of stopping the local API.
- Local data remains available when a peer is offline.
- Node status is derived from report age and a configurable timeout.

## Architecture decision record conflicts

ADR-0003, [Simulated IoT Devices](adr/ADR-0003_device-platform.md), is the governing device-platform decision and requires no physical hardware. [ADR-0004 Hybrid Deployment](adr/ADR-0003_device-platform.md) has a historical hybrid description that mentions Docker and Raspberry Pi, but the repository implementation follows the simulated-device decision and does not require Raspberry Pi. This is documentation of the conflict, not a silent replacement of architecture decisions.
