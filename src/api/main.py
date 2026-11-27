
"""MeshWatch API - device status and historical sensor readings."""

from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="MeshWatch API")


# Existing device status functionality
class DeviceStatus(BaseModel):
    device_id: str
    online: bool
    rssi: int


status_readings: list[DeviceStatus] = []


# Environmental sensor reading model
class SensorReading(BaseModel):
    device_id: str
    timestamp: datetime
    temperature_c: float | None = None
    humidity_percent: float | None = None
    light_lux: float | None = None


# Temporary in-memory storage
sensor_readings: list[SensorReading] = []


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/devices/status", status_code=201)
async def report_status(status: DeviceStatus):
    status_readings.append(status)
    return status


@app.get("/devices/status")
async def list_status():
    return status_readings


# Add a sensor reading
@app.post("/readings", status_code=201)
async def add_reading(reading: SensorReading):
    if all(
        value is None
        for value in (
            reading.temperature_c,
            reading.humidity_percent,
            reading.light_lux,
        )
    ):
        raise HTTPException(
            status_code=422,
            detail="At least one sensor value is required.",
        )

    sensor_readings.append(reading)
    return reading


# Retrieve historical sensor readings
@app.get("/readings")
async def get_historical_readings(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    sensor_type: Literal["temperature", "humidity", "light"] | None = None,
):
    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="Start time must be before or equal to end time.",
        )

    results = sensor_readings

    if start_time:
        results = [
            reading for reading in results
            if reading.timestamp >= start_time
        ]

    if end_time:
        results = [
            reading for reading in results
            if reading.timestamp <= end_time
        ]

    if sensor_type:
        field = {
            "temperature": "temperature_c",
            "humidity": "humidity_percent",
            "light": "light_lux",
        }[sensor_type]

        results = [
            reading for reading in results
            if getattr(reading, field) is not None
        ]

    return results
