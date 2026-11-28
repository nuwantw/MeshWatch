"""MeshWatch API: storage, node status, alerts, and gossip."""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.discovery import MeshWatchDiscovery
from src.storage import JSONStore

GOSSIP_TASK = None


@asynccontextmanager
async def lifespan(application: FastAPI):
    global GOSSIP_TASK
    DISCOVERY.start()
    for peer in DISCOVERY.static_peers():
        STORE.put_peer(peer)

    async def gossip_loop():
        interval = float(os.getenv("MESHWATCH_GOSSIP_INTERVAL", "10"))
        while True:
            await asyncio.sleep(interval)
            await gossip_sync()

    GOSSIP_TASK = asyncio.create_task(gossip_loop())
    try:
        yield
    finally:
        DISCOVERY.stop()
        if GOSSIP_TASK:
            GOSSIP_TASK.cancel()


app = FastAPI(title="MeshWatch API", lifespan=lifespan)

NODE_ID = os.getenv("MESHWATCH_NODE_ID", "node-1")
STORE = JSONStore()
FRONTEND_FILE = Path(__file__).resolve().parents[2] / "frontend" / "index.html"
DISCOVERY = MeshWatchDiscovery(NODE_ID)


class DeviceStatus(BaseModel):
    device_id: str
    online: bool
    rssi: int
    last_seen: datetime | None = None


status_readings: list[DeviceStatus] = []


class SensorReading(BaseModel):
    reading_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    timestamp: datetime
    temperature_c: float | None = None
    humidity_percent: float | None = None
    light_lux: float | None = None


sensor_readings: list[SensorReading] = []


class AlertRule(BaseModel):
    sensor: Literal["temperature", "humidity", "light"]
    operator: Literal["gt", "lt"]
    value: float


class Peer(BaseModel):
    node_id: str
    base_url: str


def _sync_lists_from_store() -> None:
    sensor_readings[:] = [SensorReading(**item) for item in STORE.get_readings()]
    status_readings[:] = [DeviceStatus(**item) for item in STORE.get_statuses()]


_sync_lists_from_store()


@app.get("/", include_in_schema=False)
async def dashboard():
    if not FRONTEND_FILE.is_file():
        raise HTTPException(status_code=404, detail="Dashboard frontend not found.")
    return FileResponse(FRONTEND_FILE)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/node")
async def node_info():
    return {"node_id": NODE_ID}


@app.post("/devices/status", status_code=201)
async def report_status(status: DeviceStatus):
    payload = status.model_dump(mode="json")
    payload["last_seen"] = (status.last_seen or datetime.now(timezone.utc)).isoformat()
    STORE.put_status(payload)
    stored = DeviceStatus(**payload)
    status_readings[:] = [item for item in status_readings if item.device_id != stored.device_id]
    status_readings.append(stored)
    return stored


@app.get("/devices/status")
async def list_status():
    now = datetime.now(timezone.utc)
    timeout_seconds = float(os.getenv("MESHWATCH_STATUS_TIMEOUT", "30"))
    statuses = []
    for status in status_readings:
        last_seen = status.last_seen
        online = status.online
        if last_seen:
            normalized = last_seen if last_seen.tzinfo else last_seen.replace(tzinfo=timezone.utc)
            online = (now - normalized).total_seconds() <= timeout_seconds
        statuses.append(status.model_copy(update={"online": online}))
    return statuses


@app.post("/readings", status_code=201)
async def add_reading(reading: SensorReading, replicate: bool = Query(False, include_in_schema=False)):
    if all(value is None for value in (reading.temperature_c, reading.humidity_percent, reading.light_lux)):
        raise HTTPException(status_code=422, detail="At least one sensor value is required.")

    payload = reading.model_dump(mode="json")
    stored, accepted = STORE.put_reading(payload)
    if accepted:
        sensor_readings.append(SensorReading(**stored))
    return SensorReading(**stored)


@app.post("/gossip/readings", status_code=200)
async def receive_gossip(readings: list[SensorReading]):
    payloads = [reading.model_dump(mode="json") for reading in readings]
    accepted = STORE.put_readings(payloads)
    _sync_lists_from_store()
    return {"accepted": accepted, "total": len(STORE.get_readings())}


@app.get("/gossip/readings")
async def expose_gossip_readings(limit: int = 500):
    readings = sorted(STORE.get_readings(), key=lambda item: item["timestamp"])
    return readings[-limit:] if limit > 0 else readings


@app.post("/peers", status_code=201)
async def register_peer(peer: Peer):
    payload = peer.model_dump(mode="json")
    payload["last_seen"] = datetime.now(timezone.utc).isoformat()
    return STORE.put_peer(payload)


@app.get("/peers")
async def list_peers():
    return STORE.get_peers()


@app.post("/gossip/sync", status_code=200)
async def gossip_sync():
    peers = [peer for peer in STORE.get_peers() if peer["node_id"] != NODE_ID]
    synced = 0
    errors = []
    async with httpx.AsyncClient(timeout=2.0) as client:
        for peer in peers:
            base_url = peer["base_url"].rstrip("/")
            try:
                remote = await client.get(f"{base_url}/gossip/readings", params={"limit": 1000})
                remote.raise_for_status()
                accepted = STORE.put_readings(remote.json())
                await client.post(f"{base_url}/gossip/readings", json=STORE.get_readings())
                synced += accepted
            except (httpx.HTTPError, ValueError) as error:
                errors.append({"node_id": peer["node_id"], "error": str(error)})
    _sync_lists_from_store()
    return {"synced": synced, "peers": len(peers), "errors": errors}


@app.get("/alerts")
async def get_alerts():
    thresholds = {
        "temperature_c": (float(os.getenv("ALERT_TEMP_HIGH_C", "35")), "gt", "temperature"),
        "humidity_percent": (float(os.getenv("ALERT_HUMIDITY_HIGH_PERCENT", "80")), "gt", "humidity"),
        "light_lux": (float(os.getenv("ALERT_LIGHT_HIGH_LUX", "900")), "gt", "light"),
    }
    alerts = []
    for reading in sensor_readings:
        for field, (value, operator, sensor) in thresholds.items():
            reading_value = getattr(reading, field)
            if reading_value is not None and ((operator == "gt" and reading_value > value)):
                alerts.append({
                    "reading_id": reading.reading_id,
                    "device_id": reading.device_id,
                    "sensor": sensor,
                    "value": reading_value,
                    "threshold": value,
                    "timestamp": reading.timestamp,
                })
    return alerts


@app.get("/readings")
async def get_historical_readings(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sensor_type: Literal["temperature", "humidity", "light"] | None = None,
):
    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=400, detail="Start time must be before or equal to end time.")

    results = sensor_readings
    if start_time:
        results = [reading for reading in results if reading.timestamp >= start_time]
    if end_time:
        results = [reading for reading in results if reading.timestamp <= end_time]
    if sensor_type:
        field = {"temperature": "temperature_c", "humidity": "humidity_percent", "light": "light_lux"}[sensor_type]
        results = [reading for reading in results if getattr(reading, field) is not None]
    return results
