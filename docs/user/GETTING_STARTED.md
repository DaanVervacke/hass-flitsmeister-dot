# Getting Started with Flitsmeister DOT

This guide installs the Flitsmeister DOT integration and adds your DOT to Home Assistant.

## Prerequisites

- Home Assistant 2026.10.0 or newer
- A Bluetooth adapter or an ESPHome Bluetooth proxy within range of the DOT
- A Flitsmeister DOT

## Installation

### Via the Marketplace (Home Assistant 2026.11 and newer, recommended)

1. Go to **Settings** → **Marketplace**
2. Add this repository as a custom repository: `https://github.com/DaanVervacke/hass-flitsmeister-dot`, category "Integration". The Marketplace asks you to connect a GitHub account for repositories outside its catalog.
3. Open "Flitsmeister DOT" and click "Download"

A restart is not needed for the first installation; updates and removal ask for one.

### Via HACS (before Home Assistant 2026.11)

1. Open HACS in your Home Assistant instance
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add this repository URL: `https://github.com/DaanVervacke/hass-flitsmeister-dot`
5. Set category to "Integration"
6. Click "Add"
7. Find "Flitsmeister DOT" in the list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/DaanVervacke/hass-flitsmeister-dot/releases)
2. Extract the `flitsmeister_dot` folder from the archive
3. Copy it to `custom_components/flitsmeister_dot/` in your Home Assistant configuration directory
4. Restart Home Assistant

## Initial Setup

The DOT sleeps while it is parked and only advertises after it senses motion. Pick it up or shake it first.

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Flitsmeister DOT"
4. Pick the discovered DOT, or enter its Bluetooth address
5. Home Assistant connects once to check the DOT, then finishes

## What Gets Created

### Device

One device per DOT, with the manufacturer, model, firmware version and serial number the DOT reports.

### Entities

- `sensor.flitsmeister_dot_battery`: battery level
- `sensor.flitsmeister_dot_charging`: unplugged, charging, plugged in
- `sensor.flitsmeister_dot_motion`: parked, driving
- `sensor.flitsmeister_dot_speech_language`: the voice language (diagnostic)
- `select.flitsmeister_dot_volume`, `select.flitsmeister_dot_brightness`, `select.flitsmeister_dot_led_orientation`
- `event.flitsmeister_dot_red_button`, `event.flitsmeister_dot_blue_button`: short and long presses

[CONFIGURATION.md](./CONFIGURATION.md) lists every value and both actions.

## First Steps

### Dashboard card

```yaml
type: entities
title: Flitsmeister DOT
entities:
  - sensor.flitsmeister_dot_battery
  - sensor.flitsmeister_dot_charging
  - sensor.flitsmeister_dot_motion
  - select.flitsmeister_dot_volume
```

### A first automation

Play the speed trap alert when the red button gets a short press:

```yaml
automation:
  - alias: "DOT red button plays the speed trap alert"
    trigger:
      - trigger: state
        entity_id: event.flitsmeister_dot_red_button
    condition:
      - condition: state
        entity_id: event.flitsmeister_dot_red_button
        attribute: event_type
        state: short_press
    action:
      - action: flitsmeister_dot.play_animation
        data:
          device_id: your_dot_device_id
          preset: speed_trap
```

## Troubleshooting

### Setup fails to connect

1. Wake the DOT by picking it up or shaking it
2. Keep it within Bluetooth range of the adapter or proxy Home Assistant uses
3. Close the Flitsmeister phone app, since the DOT accepts one connection at a time
4. Check the Home Assistant log for the reason

### Entities show "Unavailable"

The DOT is asleep or out of range. It reconnects on its own once it wakes up, which takes up to about a minute.

### Debug Logging

```yaml
logger:
  default: warning
  logs:
    custom_components.flitsmeister_dot: debug
    flitsmeister_dot_ble: debug
```

Add this to `configuration.yaml`, restart, and reproduce the issue.

## Next Steps

- See [CONFIGURATION.md](./CONFIGURATION.md) for every entity, action and the connection behavior
- See [EXAMPLES.md](./EXAMPLES.md) for more automation examples
- Report issues at [GitHub Issues](https://github.com/DaanVervacke/hass-flitsmeister-dot/issues)

## Support

- [GitHub Discussions](https://github.com/DaanVervacke/hass-flitsmeister-dot/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
