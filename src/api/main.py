"""MeshWatch API - minimal FastAPI backend (issue #23).

Run:  uvicorn src.api.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MeshWatch API")


class DeviceStatus(BaseModel):
    device_id: str
    online: bool
    rssi: int  # signal strength in dBm


readings: list[DeviceStatus] = []


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/devices/status", status_code=201)
async def report_status(status: DeviceStatus):
    readings.append(status)
    return status


@app.get("/devices/status")
async def list_status():
    return readings
