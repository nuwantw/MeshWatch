# Research: mDNS Peer Discovery for MeshWatch

**Related Issue:** #20  
**Status:** Research Draft 

## 1. Introduction

MeshWatch is a distributed environmental monitoring system. Each node collects or simulates temperature, humidity, and light sensor data.

The nodes must discover each other and exchange sensor readings using a gossip-based communication protocol.

The goal of this research is to understand how Multicast DNS (mDNS) works, how it can be implemented in Python, and whether it is suitable for MeshWatch.

## 2. How Does mDNS Work?

Multicast DNS (mDNS) allows devices to resolve names and discover services within a local network without requiring a central DNS server.

It uses:
- UDP port 5353
- IPv4 multicast address 224.0.0.251
- Local domain names such as `device.local`

Together with DNS-Based Service Discovery (DNS-SD), mDNS allows devices to advertise and discover services automatically.

**Example for MeshWatch:**

1. MeshWatch Node A starts and advertises its service.
2. MeshWatch Node B searches for available MeshWatch services.
3. Node B discovers Node A and obtains its IP address and port.
4. The nodes can establish a connection and exchange sensor data.

mDNS is responsible for discovering peers, not for transferring sensor readings. The actual data exchange requires a separate communication mechanism.

## 3. Implementing mDNS in Python

Python provides a library called `zeroconf`, which supports mDNS and DNS-SD.

The library can be installed using:

`pip install zeroconf`

Important components include:

| Component | Purpose |
|---|---|
| `Zeroconf` | Handles mDNS communication |
| `ServiceInfo` | Describes an advertised service |
| `register_service()` | Makes a service discoverable |
| `ServiceBrowser` | Searches for available services |

A possible implementation for MeshWatch would involve:

1. Starting the `zeroconf` service when a MeshWatch node starts.
2. Registering the node under a service type such as `_meshwatch._tcp.local.`.
3. Searching for other registered MeshWatch nodes.
4. Retrieving their network addresses and ports.
5. Passing the discovered peer information to the gossip communication component.

The service name is a proposal and still needs to be agreed upon by the team.

## 4. Advantages and Limitations

**Advantages:**
- Automatic discovery of devices within a local network.
- No manual IP address configuration required.
- No central discovery server needed for local operation.
- Python implementation is possible using an existing library.

**Limitations:**
- Standard mDNS discovery is limited to the local network link.
- It does not automatically discover devices across different home networks.
- Firewalls and network configurations can block multicast communication.
- Docker environments may require additional network configuration.
- mDNS does not provide authentication between MeshWatch nodes.

## 5. Conclusion

mDNS is a suitable approach for discovering MeshWatch nodes within a local network. Together with the Python `zeroconf` library, it provides the necessary functionality to advertise and discover services.

A small prototype with multiple simulated nodes can validate the approach in the selected development environment, especially in Docker setups where multicast communication may require additional configuration. Communication across different networks is not covered by standard mDNS and would require a separate solution if needed later.

## 6. References

1. [RFC 6762 – Multicast DNS](https://www.rfc-editor.org/rfc/rfc6762.html)
2. [RFC 6763 – DNS-Based Service Discovery](https://www.rfc-editor.org/rfc/rfc6763.html)
3. [Python Zeroconf Documentation](https://python-zeroconf.readthedocs.io/en/stable/api.html)