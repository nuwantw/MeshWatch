
import os
import random
import time
import uuid
from datetime import datetime, timezone

import httpx


def generate_reading(device_id: str | None = None):
    """Generate a JSON sensor reading with a globally unique identity."""
    return {
        "reading_id": str(uuid.uuid4()),
        "device_id": device_id or os.getenv("MESHWATCH_NODE_ID", "node-1"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": round(random.uniform(15, 35), 2),
        "humidity_percent": round(random.uniform(30, 80), 2),
        "light_lux": round(random.uniform(0, 1000), 2),
    }


def send_reading(base_url: str, reading: dict) -> bool:
    try:
        response = httpx.post(f"{base_url.rstrip('/')}/readings", json=reading, timeout=3.0)
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False


def main():
    base_url = os.getenv("MESHWATCH_API_URL", "http://127.0.0.1:8000")
    interval = float(os.getenv("MESHWATCH_INTERVAL_SECONDS", "5"))
    device_id = os.getenv("MESHWATCH_NODE_ID", "node-1")

    while True:
        reading = generate_reading(device_id)
        if send_reading(base_url, reading):
            print("Sent", reading["reading_id"])
        else:
            print("Send failed; will retry with a new reading")
        time.sleep(interval)


if __name__ == "__main__":
    main()
