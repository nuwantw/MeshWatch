import os
import socket
import threading
import time

try:
    from zeroconf import IPVersion, ServiceBrowser, ServiceInfo, ServiceStateChange, Zeroconf
except ImportError:
    Zeroconf = None


SERVICE_TYPE = "_meshwatch._tcp.local."


class MeshWatchDiscovery:
    def __init__(self, node_id: str, port: int = 8000):
        self.node_id = node_id
        self.port = port
        self.peers: dict[str, dict] = {}
        self._zeroconf = None
        self._info = None
        self._browser = None

    def start(self) -> None:
        if Zeroconf is None:
            return
        try:
            self._zeroconf = Zeroconf(ip_version=IPVersion.All)
            address = socket.gethostbyname(socket.gethostname())
            service_name = f"{self.node_id}.{SERVICE_TYPE}"
            self._info = ServiceInfo(
                SERVICE_TYPE,
                service_name,
                addresses=[socket.inet_pton(socket.AF_INET, address)],
                port=self.port,
                properties={b"node_id": self.node_id.encode("utf-8")},
            )
            self._zeroconf.register_service(self._info)

            def changed(zeroconf, service_type, name, state_change):
                if state_change not in (ServiceStateChange.Added, ServiceStateChange.Updated):
                    return
                info = zeroconf.get_service_info(service_type, name)
                if not info:
                    return
                addresses = info.parsed_addresses()
                if addresses:
                    peer_id = name.removesuffix("." + SERVICE_TYPE)
                    self.peers[peer_id] = {
                        "node_id": peer_id,
                        "base_url": f"http://{addresses[0]}:{info.port}",
                    }

            self._browser = ServiceBrowser(self._zeroconf, SERVICE_TYPE, handlers=[changed])
        except Exception:
            self.stop()

    def stop(self) -> None:
        if self._zeroconf:
            if self._info:
                try:
                    self._zeroconf.unregister_service(self._info)
                except Exception:
                    pass
            self._zeroconf.close()
            self._zeroconf = None

    def static_peers(self) -> list[dict]:
        peers = []
        for item in os.getenv("MESHWATCH_PEERS", "").split(","):
            item = item.strip()
            if item:
                peers.append({"node_id": item.split("://")[-1], "base_url": item})
        peers.extend(self.peers.values())
        unique = {peer["node_id"]: peer for peer in peers}
        return list(unique.values())
