from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_report_and_list_status():
    r = client.post("/devices/status", json={"device_id": "node-1", "online": True, "rssi": -60})
    assert r.status_code == 201
    ids = [d["device_id"] for d in client.get("/devices/status").json()]
    assert "node-1" in ids


def test_invalid_payload_rejected():
    r = client.post("/devices/status", json={"device_id": "node-1"})
    assert r.status_code == 422
