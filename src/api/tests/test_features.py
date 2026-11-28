import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from src.api.main import app, sensor_readings, status_readings, STORE
from src.sensor_simulator import generate_reading
from src.storage import JSONStore


client = TestClient(app)


def setup_function():
    sensor_readings.clear()
    status_readings.clear()
    STORE.clear()


def test_duplicate_reading_is_rejected_as_a_duplicate_by_id():
    reading = {
        "reading_id": "reading-1",
        "device_id": "node-1",
        "timestamp": "2026-01-01T10:00:00Z",
        "temperature_c": 21.0,
    }
    first = client.post("/readings", json=reading)
    duplicate = client.post("/readings", json=reading)

    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert len(client.get("/readings").json()) == 1


def test_gossip_accepts_only_new_readings():
    readings = [
        {
            "reading_id": "gossip-1",
            "device_id": "node-2",
            "timestamp": "2026-01-01T10:00:00Z",
            "humidity_percent": 45.0,
        },
        {
            "reading_id": "gossip-2",
            "device_id": "node-3",
            "timestamp": "2026-01-01T10:01:00Z",
            "light_lux": 300.0,
        },
    ]

    response = client.post("/gossip/readings", json=readings)
    repeated = client.post("/gossip/readings", json=readings)

    assert response.json()["accepted"] == 2
    assert repeated.json()["accepted"] == 0
    assert len(client.get("/readings").json()) == 2


def test_persistence_survives_store_recreation():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "node.json"
        first_store = JSONStore(path)
        reading = {
            "reading_id": "persist-1",
            "device_id": "node-persist",
            "timestamp": "2026-01-01T10:00:00Z",
            "temperature_c": 23.0,
        }
        first_store.put_reading(reading)

        restored_store = JSONStore(path)

        assert restored_store.get_readings() == [reading]


def test_simulator_generates_unique_reading_ids():
    first = generate_reading("node-test")
    second = generate_reading("node-test")

    assert first["device_id"] == "node-test"
    assert first["reading_id"] != second["reading_id"]
    assert {"temperature_c", "humidity_percent", "light_lux"}.issubset(first)


def test_offline_peer_is_reported_without_stopping_local_api():
    peer = client.post("/peers", json={"node_id": "offline-node", "base_url": "http://127.0.0.1:65534"})
    sync = client.post("/gossip/sync")

    assert peer.status_code == 201
    assert sync.status_code == 200
    assert sync.json()["peers"] == 1
    assert sync.json()["errors"]
    assert client.get("/health").json() == {"status": "ok"}


def test_alert_endpoint_detects_high_temperature():
    client.post("/readings", json={
        "reading_id": "alert-1",
        "device_id": "node-alert",
        "timestamp": "2026-01-01T10:00:00Z",
        "temperature_c": 99.0,
    })

    alerts = client.get("/alerts").json()

    assert len(alerts) == 1
    assert alerts[0]["sensor"] == "temperature"
