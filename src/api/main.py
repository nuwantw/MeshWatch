
import pytest
from fastapi.testclient import TestClient

from src.api.main import app, sensor_readings, status_readings

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    sensor_readings.clear()
    status_readings.clear()
    yield
    sensor_readings.clear()
    status_readings.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_and_list_status():
    response = client.post(
        "/devices/status",
        json={"device_id": "node-1", "online": True, "rssi": -60},
    )
    assert response.status_code == 201

    response = client.get("/devices/status")
    assert response.status_code == 200
    assert response.json()[0]["device_id"] == "node-1"


def test_invalid_payload_rejected():
    response = client.post(
        "/devices/status",
        json={"device_id": "node-1"},
    )
    assert response.status_code == 422


def test_add_sensor_reading():
    response = client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T10:00:00",
            "temperature_c": 22.5,
            "humidity_percent": 55.0,
            "light_lux": 300.0,
        },
    )
    assert response.status_code == 201
    assert response.json()["device_id"] == "node-1"
    assert response.json()["temperature_c"] == 22.5
    assert response.json()["timestamp"] == "2026-11-28T10:00:00"


def test_reject_reading_without_sensor_values():
    response = client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T10:00:00",
        },
    )
    assert response.status_code == 422


def test_retrieve_historical_readings():
    client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T10:00:00",
            "temperature_c": 22.5,
        },
    )

    response = client.get("/readings")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["temperature_c"] == 22.5


def test_filter_readings_by_sensor_type():
    client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T10:00:00",
            "temperature_c": 22.5,
            "humidity_percent": 55.0,
        },
    )

    response = client.get(
        "/readings",
        params={"sensor_type": "temperature"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_readings_by_time_range():
    client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T10:00:00",
            "temperature_c": 22.5,
        },
    )

    client.post(
        "/readings",
        json={
            "device_id": "node-1",
            "timestamp": "2026-11-28T12:00:00",
            "temperature_c": 25.0,
        },
    )

    response = client.get(
        "/readings",
        params={
            "start_time": "2026-11-28T11:00:00",
            "end_time": "2026-11-28T13:00:00",
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["temperature_c"] == 25.0


def test_invalid_time_range_rejected():
    response = client.get(
        "/readings",
        params={
            "start_time": "2026-11-28T13:00:00",
            "end_time": "2026-11-28T10:00:00",
        },
    )

    assert response.status_code == 400
