ADR-0004: Hybrid Deployment with Docker and Raspberry Pi

Status: Accepted
Date: 2026-11-11
Author: Usman Akhtar

Context

MeshWatch needs to run on Windows, macOS, and physical IoT hardware while supporting automated testing with real sensors.

Considered Options

Physical hardware only: Realistic but expensive and difficult to test.

Docker only: Portable but lacks physical sensor integration.

Hybrid approach: Combines simulated Docker nodes with a Raspberry Pi.

Decision

We will use a hybrid architecture:

Docker Compose for simulated nodes on Windows and macOS.

Raspberry Pi for one physical node with real sensors.

Python for shared application logic. 
Decision may change during the process.

Consequences

Positive:

Cross-platform development.

Testing without physical hardware.

Real sensor integration.

Low hardware costs.

Negative:

Additional Raspberry Pi configuration.

Docker networking and mDNS require special attention.
