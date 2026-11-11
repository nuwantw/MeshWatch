# ADR-0005: Data Format

## Context

MeshWatch collects sensor data and shares it between
devices, the backend, and the web interface.

We need a common data format that is easy to use
and understand.

We considered JSON, CBOR, and Protobuf.

## Decision

We will use JSON because it is easy to read and
works well with Python and JavaScript.

We will follow these rules:

- Devices and the backend will exchange sensor data in JSON.
- The backend will send data to the web interface in JSON.
- Each reading will include a device ID, timestamp,
  and sensor values with their units.
- Incoming data will be checked before it is used.

## Status

Proposed.

## Consequences

JSON makes development, testing, and debugging easier
because messages are readable.

However, JSON messages can be larger than CBOR or
Protobuf messages and use more network bandwidth.

We may reconsider the format later if message size
becomes a problem.
