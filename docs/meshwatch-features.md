
# MeshWatch – Main Features and Project Structure

## 1. Project Overview

MeshWatch is a distributed IoT platform designed to monitor environmental conditions such as temperature, humidity, and light.

The system consists of multiple IoT devices, called nodes, that communicate with each other over a local network. Each node collects environmental measurements using physical sensors.

Instead of sending all measurements to one central server, MeshWatch uses a decentralized approach. Nodes automatically discover each other and exchange their collected data using a gossip protocol.

This allows each node to maintain information about other nodes in the network. If one node becomes unavailable, its previously shared measurements can still be accessed through other nodes.

Users can access a web dashboard from any available node to view environmental measurements from the entire network.

For the initial development, MeshWatch will use simulated IoT devices. This allows the team to develop and test the platform without requiring physical hardware.

The project focuses on distributed communication, environmental monitoring, data availability, and reliable software development.

## 2. Main Features

### 2.1 Sensor Simulation
Generate simulated temperature, humidity, and light measurements using Python. This allows testing without physical IoT sensors.

### 2.2 Peer Discovery (mDNS)
Automatically discover other MeshWatch nodes on the local network using mDNS.

### 2.3 Gossip Protocol
Exchange sensor measurements between nodes using a gossip-based communication protocol without relying on a central server.

### 2.4 Data Storage
Store local and received sensor measurements so that previously shared data remains available when another node goes offline.

### 2.5 Web Dashboard
Provide a simple web interface using HTML, CSS, and JavaScript to display environmental measurements from all nodes.

### 2.6 Alerting System
Detect sensor measurements that exceed predefined thresholds, such as unusually low/high temperatures or humidity levels.

### 2.7 Multiple Node Support
Allow multiple simulated IoT nodes to operate simultaneously and communicate within the same network.

### 2.8 Node Status Monitoring
Display whether nodes are currently active or unavailable based on their last known communication.


### 2.9 Configuration and Setup
Provide configuration options for node identifiers, communication settings, and sensor parameters, together with instructions for starting the system.

## 3. Proposed Project Structure

The following folder structure is proposed to organize the different components of MeshWatch.

- `simulator/` – Simulated environmental sensors
- `discovery/` – mDNS peer discovery
- `gossip/` – Communication and data replication between nodes
- `storage/` – Local and replicated sensor data
- `backend/` – API endpoints and server logic
- `frontend/` – Web dashboard using HTML, CSS, and JavaScript
- `alerts/` – Environmental monitoring and alert rules
- `config/` – Node and application configuration
- `tests/` – Unit and integration tests
- `docs/` – Project documentation and ADRs


This structure is a proposal and should be reviewed against the existing Architecture Decision Records (ADRs) before implementation.
