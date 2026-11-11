# Architecture Overview

This document describes the technical architecture of the Flitsmeister DOT custom component for Home Assistant.

## Directory Structure

```text
custom_components/flitsmeister_dot/
├── __init__.py              # Integration setup, unload and PLATFORMS
├── config_flow.py           # Config flow entry point
├── const.py                 # Constants
├── coordinator/             # The BLE session coordinator
│   ├── __init__.py          # Exports FlitsmeisterDotCoordinator
│   └── base.py              # Connects, pushes values, reconnects
├── data.py                  # The typed config entry
├── diagnostics.py           # Redacted diagnostics
├── entity/                  # Base entity package
│   ├── __init__.py          # Exports FlitsmeisterDotEntity
│   └── base.py              # Device info, unique IDs, write errors
├── icons.json               # Entity and action icons
├── manifest.json            # Integration metadata and Bluetooth matchers
├── repairs.py               # Repair flows
├── services.yaml            # Action definitions (legacy filename)
├── config_flow_handler/     # Config flow implementation
│   ├── __init__.py          # Package exports
│   ├── config_flow.py       # Bluetooth discovery, picker, manual address
│   ├── schemas/             # probatio schemas
│   │   ├── __init__.py
│   │   └── config.py        # Address and picker forms
│   └── validators/
│       ├── __init__.py
│       └── device.py        # Address format check and one test connection
├── event/                   # Red and blue button event entities
├── select/                  # Volume, brightness, LED orientation
├── sensor/                  # Battery, charging, motion, speech language
├── service_actions/         # Actions, registered in async_setup()
│   ├── __init__.py
│   ├── play_animation.py
│   ├── play_progress.py
│   └── presets.py           # Preset name to library animation
├── translations/
│   └── en.json
└── utils/
    └── dot_errors.py        # Library errors to translated user errors
```

There is no `api/` package. The device protocol lives in the PyPI library
[`flitsmeister-dot-ble`](https://pypi.org/project/flitsmeister-dot-ble/), which plays the role of the API client.

## Core Components

### Session Coordinator

**Directory:** `coordinator/`

The coordinator holds one Bluetooth session with the DOT and pushes every decoded value to the entities, so no entity
ever talks to the device itself.

**Core functionality:**

- No update interval. The DOT pushes values over the live connection, and `async_set_updated_data` hands them on.
  Notifications that change nothing are dropped, so unchanged values do not rewrite every state.
- The connect sequence writes the stored volume, plays the startup animation and reads the settings, like the app.
- A lost session marks every entity unavailable and starts a reconnect loop: right away, then after 5, 10, 30 and
  every 60 seconds (`RECONNECT_DELAYS`), as long as Home Assistant still sees the DOT. A new advertisement restarts the
  loop once the DOT was out of reach.
- Unloading the entry cancels the loop and any connect attempt still running.

**Key class:** `FlitsmeisterDotCoordinator` (exported from `coordinator/__init__.py`)

Home Assistant only reports an advertisement when its content changes, and the DOT always sends the same one. That is
why the coordinator cannot wait for advertisements to reconnect, and runs its own loop instead.

### Device Library

The protocol, the connection lifecycle and the button press resolution come from `flitsmeister-dot-ble`. The
coordinator only calls its `FlitsmeisterDotClient`. `utils/dot_errors.py` turns the library's errors into translated
Home Assistant errors for entities and actions.

### Config Flow

**Directory:** `config_flow_handler/`

Implements the configuration UI for adding and configuring the integration. The package
is organized modularly to support complex flows without becoming monolithic.

**Structure:**

- `config_flow.py`: Bluetooth discovery, a picker for discovered DOTs and manual address entry
- `schemas/`: probatio schemas for the forms
- `validators/`: the address format check and one test connection to the DOT

**Supported flows:**

- Bluetooth discovery with a confirm step
- Picking a discovered DOT
- Manual address entry, checked by connecting once

There is no options flow, reauth or reconfigure: the DOT has no credentials and no settings that live in the config
entry.

**Key class:** `FlitsmeisterDotConfigFlowHandler`

### Base Entity

**Package:** `entity/`

Provides common functionality for all entities in the integration:

- Device information
- Unique ID generation
- Coordinator integration
- Availability tracking

**Key class:** `FlitsmeisterDotEntity` (in `entity/base.py`)

## Platform Organization

Each platform (sensor, select, event) follows this pattern:

```text
<platform>/
├── __init__.py              # Platform setup: async_setup_entry()
└── <entity_name>.py         # Individual entity implementation
```

Platform entities inherit from both:

1. Home Assistant platform base (e.g., `SensorEntity`)
2. `FlitsmeisterDotEntity` for common functionality

## Data Flow

```text
┌─────────────────┐
│  Config Entry   │ ← Created by config flow
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Coordinator   │ ← Holds the BLE session, receives pushed values
└────────┬────────┘
         │
         ▼
    ┌────┴────┐
    │  Data   │ ← Stored in coordinator.data
    └────┬────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│ Sensor  │         │ Select  │ ← Entities read from coordinator
└─────────┘         └─────────┘
```

## AI Agent Context

Agent-facing content is layered so each piece is loaded only when it is relevant:

| Layer                             | Loaded                      | Contains                                          |
| --------------------------------- | --------------------------- | ------------------------------------------------- |
| `AGENTS.md`                       | always                      | project identity, workflow rules, validation loop |
| `.agents/instructions/*.md`       | per touched file            | passive style rules for one file type             |
| `.agents/skills/*/SKILL.md`       | when a task matches         | active procedures for a specific kind of work     |
| `docs/development/`, `docs/user/` | when a human or agent reads | explanations, decisions, guides — this document   |

Style rules belong in `.agents/instructions/`, procedures belong in a skill, explanations belong in `docs/`.

One copy of each instruction file serves two agents: GitHub Copilot and VS Code match its `applyTo` glob string,
Claude Code matches the same patterns via `paths` (a YAML list, one pattern per item) and reaches the same files
through the `.claude/rules/instructions` symlink. Codex and OpenCode have no comparable file-triggered mechanism —
their nested `AGENTS.md` support keys off the working directory or the files read, not on file-type patterns — so
they rely on the root `AGENTS.md` plus the pointers each skill carries.

The skill catalogue, the symlink layout that makes one directory work for every agent vendor, and the rules for writing
a new skill are documented in [`.agents/skills/README.md`](../../.agents/skills/README.md).

For working with AI coding agents in this repository, see [`AI_AGENTS.md`](./AI_AGENTS.md).

## Key Design Decisions

See [DECISIONS.md](./DECISIONS.md) for architectural and design decisions made during development.

## Extension Points

To add new functionality:

### Adding a New Platform

1. Create directory: `custom_components/flitsmeister_dot/<platform>/`
2. Implement `__init__.py` with `async_setup_entry()`
3. Create entity classes inheriting from platform base + `FlitsmeisterDotEntity`
4. Add platform to `PLATFORMS` in `__init__.py`

### Adding a New Service Action

1. Create service action handler in `service_actions/<service_name>.py`
2. Define service action in `services.yaml` (legacy filename) with schema
3. Register service action in `__init__.py:async_setup()` (NOT `async_setup_entry`)

### Exposing a New Device Value

1. Add the value to the library's `DotState` in `flitsmeister-dot-ble` and release it
2. Raise the `flitsmeister-dot-ble` requirement in `manifest.json` and `requirements.txt`
3. Add an entity description whose `value_fn` reads the new field

## Testing Strategy

- **Unit tests:** Test individual functions and classes in isolation
- **Integration tests:** Set up the entry against an in-memory fake DOT (`FakeDotClient` in `tests/conftest.py`)
  and a fake Bluetooth layer that fires advertisements and takes the DOT out of reach
- **Fixtures:** Shared test fixtures in `tests/conftest.py`

Tests mirror the source structure under `tests/`.

## Dependencies

Core dependencies (see `manifest.json`):

- `flitsmeister-dot-ble` - The DOT protocol and BLE client
- The `bluetooth` integration - Discovery, scanners and connections
- Home Assistant 2026.10.0+ - Platform requirements

Development dependencies (see `requirements_dev.txt`, `requirements_test.txt`).
