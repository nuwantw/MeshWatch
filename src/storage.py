import json
import os
import threading
from pathlib import Path
from typing import Iterable


class JSONStore:
    """Small thread-safe JSON persistence layer for a single MeshWatch node."""

    def __init__(self, path: str | Path | None = None):
        configured = path or os.getenv("MESHWATCH_DATA_FILE", "data/meshwatch.json")
        self.path = Path(configured)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.readings: dict[str, dict] = {}
        self.statuses: dict[str, dict] = {}
        self.peers: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
            self.readings = data.get("readings", {})
            self.statuses = data.get("statuses", {})
            self.peers = data.get("peers", {})
        except (json.JSONDecodeError, OSError):
            self.readings = {}
            self.statuses = {}
            self.peers = {}

    def _save(self) -> None:
        payload = {
            "readings": self.readings,
            "statuses": self.statuses,
            "peers": self.peers,
        }
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        temporary.replace(self.path)

    def clear(self) -> None:
        with self._lock:
            self.readings.clear()
            self.statuses.clear()
            self.peers.clear()
            self._save()

    def put_reading(self, reading: dict) -> tuple[dict, bool]:
        with self._lock:
            reading_id = reading["reading_id"]
            if reading_id in self.readings:
                return self.readings[reading_id], False
            self.readings[reading_id] = reading
            self._save()
            return reading, True

    def put_readings(self, readings: Iterable[dict]) -> int:
        accepted = 0
        with self._lock:
            for reading in readings:
                reading_id = reading["reading_id"]
                if reading_id not in self.readings:
                    self.readings[reading_id] = reading
                    accepted += 1
            if accepted:
                self._save()
        return accepted

    def get_readings(self) -> list[dict]:
        with self._lock:
            return list(self.readings.values())

    def put_status(self, status: dict) -> dict:
        with self._lock:
            self.statuses[status["device_id"]] = status
            self._save()
            return status

    def get_statuses(self) -> list[dict]:
        with self._lock:
            return list(self.statuses.values())

    def put_peer(self, peer: dict) -> dict:
        with self._lock:
            peer_id = peer["node_id"]
            self.peers[peer_id] = peer
            self._save()
            return peer

    def get_peers(self) -> list[dict]:
        with self._lock:
            return list(self.peers.values())
