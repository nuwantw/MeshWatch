# MeshWatch

MeshWatch is a decentralized environmental monitoring platform with simulated IoT nodes, mDNS peer discovery, JSON gossip replication, persistent storage, alerts, node status monitoring, and an HTML/JavaScript dashboard.

## Quick start

```bash
python -m pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://127.0.0.1:8000`. API documentation is at `http://127.0.0.1:8000/docs`.

Generate readings locally:

```bash
python -m src.sensor_simulator
```

Set `MESHWATCH_API_URL` to point the simulator at another node.

## Multi-node Docker setup

```bash
docker compose up --build
```

Nodes and dashboards:

- Node 1: `http://127.0.0.1:8001`
- Node 2: `http://127.0.0.1:8002`
- Node 3: `http://127.0.0.1:8003`

Each node has a named Docker volume for local JSON persistence. Each simulator sends readings to its own node every few seconds. Nodes exchange readings through HTTP gossip endpoints and static Compose peer URLs.

Stop and remove containers but retain node data:

```bash
docker compose down
```

Remove persisted data too:

```bash
docker compose down -v
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `MESHWATCH_NODE_ID` | `node-1` | Unique node identifier |
| `MESHWATCH_DATA_FILE` | `data/meshwatch.json` | Persistent JSON store |
| `MESHWATCH_PEERS` | empty | Comma-separated peer base URLs |
| `MESHWATCH_GOSSIP_INTERVAL` | `10` | Seconds between gossip cycles |
| `MESHWATCH_STATUS_TIMEOUT` | `30` | Seconds before a status report is unavailable |
| `MESHWATCH_API_URL` | `http://127.0.0.1:8000` | Simulator destination |
| `MESHWATCH_INTERVAL_SECONDS` | `5` | Simulator reading interval |
| `ALERT_TEMP_HIGH_C` | `35` | High-temperature threshold |
| `ALERT_HUMIDITY_HIGH_PERCENT` | `80` | High-humidity threshold |
| `ALERT_LIGHT_HIGH_LUX` | `900` | High-light threshold |

## Tests

```bash
python -m pytest -v
```

The suite covers the existing API contract, historical filtering, duplicate readings, JSON persistence, gossip, offline peers, alerts, and simulated readings.

## Architecture notes

ADR-0003 governs this implementation: no physical ESP32 or Raspberry Pi hardware is required, and devices are simulated. ADR-0004 is a historical hybrid deployment decision that mentions Raspberry Pi and Docker; it remains documented but is not required for the implemented solution. Docker peer discovery uses static Compose URLs because standard multicast mDNS can be restricted by container networks. Zeroconf is also available for compatible local-network discovery.
