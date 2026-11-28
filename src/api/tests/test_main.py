
def test_historical_sensor_readings():
    readings = [
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T10:00:00",
            "temperature_c": 22.5,
            "humidity_percent": 40.0,
            "light_lux": 100.0,
        },
        {
            "device_id": "history-node",
            "timestamp": "2026-01-01T11:00:00",
            "temperature_c": 23.0,
            "humidity_percent": 45.0,
            "light_lux": 120.0,
        },
    ]

    for reading in readings:
        response = client.post("/readings", json=reading)
        assert response.status_code == 201

    response = client.get(
        "/readings",
        params={
            "start_time": "2026-01-01T10:30:00",
            "end_time": "2026-01-01T11:30:00",
            "sensor_type": "humidity",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["device_id"] == "history-node"
    assert data[0]["humidity_percent"] == 45.0
    assert data[0]["timestamp"] == "2026-01-01T11:00:00"


def test_empty_sensor_reading_rejected():
    response = client.post(
        "/readings",
        json={
            "device_id": "history-node",
            "timestamp": "2026-01-01T12:00:00",
        },
    )

    assert response.status_code == 422


def test_invalid_historical_time_range():
    response = client.get(
        "/readings",
        params={
            "start_time": "2026-01-02T12:00:00",
            "end_time": "2026-01-01T12:00:00",
        },
    )

    assert response.status_code == 400
