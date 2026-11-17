
# ADR-0003: Simulated IoT Devices

## Context

Our team is developing MeshWatch, an IoT platform
that collects and monitors sensor data from devices.

We need to decide whether to use physical hardware
or simulated devices to generate sensor readings.

We considered ESP32, Raspberry Pi, and simulated
IoT devices.

## Decision

We will use simulated IoT devices instead of
physical hardware because our project does not
require real sensors or physical devices.

We will follow these rules:

- Devices will be simulated using software.
- Each simulated device will have a unique device ID.
- Devices will generate sensor data such as
  temperature and humidity.
- Simulated devices will send data to the
  MeshWatch platform.
- We will simulate multiple devices for testing.
- No physical ESP32 or Raspberry Pi boards are
  required.

## Status

Accepted.

## Consequences

Simulation reduces project costs and makes
development and testing easier.

We can simulate multiple devices without buying
physical hardware.

However simulated devices cannot reproduce all
real world sensor behaviour and hardware limitations.
