# Architectural and Design Decisions

This document records significant architectural and design decisions made during the development of this integration.

## Format

Each decision is documented with:

- **Date:** When the decision was made
- **Context:** Why this decision was necessary
- **Decision:** What was decided
- **Rationale:** Why this approach was chosen
- **Consequences:** Expected impacts and trade-offs

> [!NOTE]
> Guidance on _when_ a decision is worth recording here, and a copy-ready entry template, lives in the
> [`ha-planning`](../../.agents/skills/ha-planning/SKILL.md) agent skill.

---

## Decision Log

### Use flitsmeister-dot-ble from PyPI instead of writing a client

**Date:** 2026-11-11

**Context:** The DOT speaks a proprietary BLE protocol reverse engineered from the Flitsmeister Android app. The maintainer's own [flitsmeister-dot-ble](https://github.com/DaanVervacke/flitsmeister-dot-ble) library already wraps it: connection lifecycle, notification decoding, button press resolution, animation presets and settings writes, with a transport interface that keeps it testable.

**Decision:** Require `flitsmeister-dot-ble>=0.1.0` and build no client of our own. The library is published to PyPI so the manifest requirement installs cleanly.

**Rationale:**

- The protocol knowledge lives in the library, maintained next to its PROTOCOL.md, instead of being copied into the integration
- The transport interface lets the test suite run against an in-memory fake
- bleak and bleak-retry-connector pins match Home Assistant's own, so no dependency conflicts

**Consequences:**

- A firmware update breaks the library first, and the integration follows its releases
- The integration holds no wire-format code, so protocol fixes ship without touching this repository

---

### Stay connected while the DOT is awake, unavailable while it sleeps

**Date:** 2026-11-11

**Context:** The DOT sleeps while parked and advertises in bursts after accelerometer motion. It drops a connection that only subscribes and reads after about 4 seconds, and it accepts one connection at a time, so Home Assistant and the phone app exclude each other.

**Decision:** The coordinator listens for advertisements, connects when the DOT wakes and stays connected, pushing every decoded value to the entities. A lost session marks the entities unavailable and starts a reconnect loop with growing delays, because Home Assistant only reports an advertisement when its content changes and the DOT always sends the same one. The connect sequence writes the stored volume and plays the startup animation, like the app, which also keeps the link past the idle drop.

**Rationale:**

- Button events only arrive over a live connection, and animations play instantly instead of after a connect delay
- Session state, not advertisement presence, drives availability: a connected DOT that stopped advertising must not flip to unavailable
- Entities honestly show unavailable while the DOT sleeps in a parked car instead of serving stale values

**Consequences:**

- The phone app cannot connect while Home Assistant holds the DOT
- Battery history has gaps for every parked period
- The coordinator is a push coordinator with no update interval, not a polling one

---

### Use DataUpdateCoordinator for All Data Fetching

**Date:** 2025-11-29 (Template initialization)

**Status:** Superseded by "Stay connected while the DOT is awake". The coordinator is still a `DataUpdateCoordinator`, but it is pushed to, with no update interval.

**Context:** The integration needs to fetch data from an external API and share it with multiple entities. Home Assistant provides several patterns for this.

**Decision:** Use `DataUpdateCoordinator` from `homeassistant.helpers.update_coordinator` as the central data management component.

**Rationale:**

- Provides built-in support for update intervals and error handling
- Automatic retry with exponential backoff
- Shared data access prevents duplicate API calls
- Standard pattern recommended by Home Assistant
- Entities automatically become unavailable when coordinator fails

**Consequences:**

- All entities must inherit from `CoordinatorEntity`
- Single update interval applies to all entities
- Data is fetched even if no entities are enabled
- Coordinator manages entity lifecycle and availability

---

### Separate API Client from Coordinator

**Date:** 2025-11-29 (Template initialization)

**Status:** Superseded by "Use flitsmeister-dot-ble from PyPI". There is no `api/` package, and the library plays the role of the client.

**Context:** The coordinator needs to fetch data, but business logic should be separated from data transport.

**Decision:** Implement API communication in separate `api/client.py` module, coordinator only orchestrates updates.

**Rationale:**

- Separation of concerns: transport vs. orchestration
- Easier to test API client in isolation
- Simpler to swap API implementation if needed
- Clearer error handling boundaries

**Consequences:**

- Additional abstraction layer
- Coordinator depends on API client
- API client raises custom exceptions for error translation

---

### Platform-Specific Directories

**Date:** 2025-11-29 (Template initialization)

**Context:** Integration supports multiple platforms (sensor, binary_sensor, switch, etc.).

**Decision:** Each platform gets its own directory with individual entity files.

**Rationale:**

- Clear organization as integration grows
- Easier to find specific entity implementations
- Supports multiple entities per platform cleanly
- Follows Home Assistant Core pattern

**Consequences:**

- More files/directories than single-file approach
- Platform `__init__.py` must import and register entities
- Slightly more initial setup overhead

---

### EntityDescription for Static Metadata

**Date:** 2025-11-29 (Template initialization)

**Context:** Entities have static metadata (name, icon, device class) that doesn't change.

**Decision:** Use `EntityDescription` dataclasses to define static entity metadata.

**Rationale:**

- Declarative and easy to read
- Type-safe with dataclasses
- Recommended Home Assistant pattern
- Separates static configuration from dynamic behavior

**Consequences:**

- Each entity type needs an EntityDescription
- Dynamic entities need custom handling
- Static and dynamic properties clearly separated

---

## Future Considerations

### State Restoration

**Status:** Implemented for the volume

The DOT never reports its volume, so the volume select restores its last state after a restart and the coordinator writes it on every connect. Brightness and orientation are read back from the DOT and need no restoration.

### Multi-Device Support

**Status:** One config entry per DOT

Every DOT is its own config entry with its own coordinator and device, keyed by its Bluetooth address.

### Polling vs. Push

**Status:** Push

The DOT pushes its values over a live BLE session. See "Stay connected while the DOT is awake".

---

## Decision Review

These decisions should be reviewed periodically (suggested: quarterly or when major features are added) to ensure they still serve the integration's needs.
