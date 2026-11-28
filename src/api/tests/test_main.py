
import pytest
from fastapi.testclient import TestClient

from src.api.main import app, sensor_readings, status_readings

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_test_data():
    """Clear stored data before every test."""
    sensor_readings.clear()
    status_readings.clear()


# --------------------------------------------------
# Basic API tests
# --------------------------------------------------

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_report_and_list_status():
    response = client.post(
        "/devices/status",
        json={
            "device_id": "node-1",
            "online": True,
            "rssi": -60
        }
    )

    assert response.status_code == 201

    result = client.get("/devices/status")

    assert result.status_code == 200
    assert result.json()[0]["device_id"] == "node-1"


def test_invalid_status_payload():
    response = client.post(
        "/devices/status",
        json={"device_id": "node-1"}
    )

    assert response.status_code == 422


# --------------------------------------------------
# Historical sensor retrieval tests
# --------------------------------------------------

def test_historical_sensor_readings():
    readings = [
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T10:00:00",
            "temperature_c": 22.5,
            "humidity_percent": 40.0,
            "light_lux": 100.0
        },
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T11:00:00",
            "temperature_c": 23.0,
            "humidity_percent": 45.0,
            "light_lux": 120.0
        }
    ]

    for reading in readings:
        response = client.post("/readings", json=reading)
        assert response.status_code == 201

    response = client.get("/readings")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["temperature_c"] == 22.5
    assert data[1]["temperature_c"] == 23.0
    assert data[0]["timestamp"] == "2026-01-01T10:00:00"


def test_time_range_filtering():
    readings = [
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T09:00:00",
            "temperature_c": 20.0
        },
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T10:00:00",
            "temperature_c": 22.0
        },
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T11:00:00",
            "temperature_c": 24.0
        }
    ]

    for reading in readings:
        client.post("/readings", json=reading)

    response = client.get(
        "/readings",
        params={
            "start_time": "2026-01-01T10:00:00",
            "end_time": "2026-01-01T11:00:00"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["temperature_c"] == 22.0
    assert data[1]["temperature_c"] == 24.0


@pytest.mark.parametrize(
    ("sensor_type", "expected_count"),
    [
        ("temperature", 1),
        ("humidity", 2),
        ("light", 1)
    ]
)
def test_sensor_type_filtering(sensor_type, expected_count):
    readings = [
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T10:00:00",
            "temperature_c": 22.5,
            "humidity_percent": 40.0,
            "light_lux": 100.0
        },
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T11:00:00",
            "humidity_percent": 45.0
        }
    ]

    for reading in readings:
        client.post("/readings", json=reading)

    response = client.get(
        "/readings",
        params={"sensor_type": sensor_type}
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == expected_count

    field = {
        "temperature": "temperature_c",
        "humidity": "humidity_percent",
        "light": "light_lux"
    }[sensor_type]

    for reading in data:
        assert reading[field] is not None
        assert reading["timestamp"] is not None


def test_empty_sensor_reading_rejected():
    response = client.post(
        "/readings",
        json={
            "device_id": "history-node",
            "timestamp": "2026-01-01T12:00:00"
        }
    )

    assert response.status_code == 422


def test_invalid_historical_time_range():
    response = client.get(
        "/readings",
        params={
            "start_time": "2026-01-02T12:00:00",
            "end_time": "2026-01-01T12:00:00"
        }
    )

    assert response.status_code == 400


def test_empty_historical_readings():
    response = client.get("/readings")

    assert response.status_code == 200
    assert response.json() == []
