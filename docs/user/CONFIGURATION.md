# Configuration Reference

This document describes how the Flitsmeister DOT integration is set up, which entities and actions it provides, and
how it behaves while the DOT sleeps.

## Setup

The integration talks to the DOT over Bluetooth Low Energy. There is nothing to sign in to: no account, password or
API key.

### Adding the DOT

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** and search for "Flitsmeister DOT"
3. Pick the DOT from the discovered devices, or choose **Enter the Bluetooth address** and type it, like
   `AA:BB:CC:DD:EE:FF`

Home Assistant connects to the DOT once before it finishes, to check that the address really reaches a DOT. The DOT
sleeps while it is parked and only answers after it senses motion, so pick it up or shake it before you start.

A DOT that advertises nearby is also offered automatically under **Settings** → **Devices & Services** as a discovered
device.

### Setup fields

| Field                 | Required | Description                                                    |
| --------------------- | -------- | -------------------------------------------------------------- |
| **Bluetooth address** | Yes      | The address of the DOT, only asked when you skip the discovery |

There are no options to change after setup. The integration has no options dialog.

### More than one DOT

Add each DOT as its own integration entry. Every DOT gets its own device and entities.

## Entities

| Entity          | Type   | Values                                      |
| --------------- | ------ | ------------------------------------------- |
| Battery         | sensor | 0 to 100 %                                  |
| Charging        | sensor | Unplugged, Charging, Plugged in             |
| Motion          | sensor | Parked, Driving                             |
| Speech language | sensor | English, Dutch, German, French (diagnostic) |
| Volume          | select | Silent, Low, Normal, Hard                   |
| Brightness      | select | 10 % to 100 % in steps of 10                |
| LED orientation | select | Normal, Upside down                         |
| Red button      | event  | Short press, Long press                     |
| Blue button     | event  | Short press, Long press                     |

"Plugged in" means USB power is connected while the charger is outside its main charging phase. The battery level can
still rise in that state, so it does not mean the battery is full.

The DOT never reports its volume back. Home Assistant remembers the volume you chose and writes it every time the DOT
connects, also after a restart.

Manufacturer, model, firmware version and serial number appear on the device page, not as entities.

## Actions

Both actions target the DOT device and fail with a clear error while the DOT is asleep.

### `flitsmeister_dot.play_animation`

Plays one of the alerts the Flitsmeister app shows, with the same LED pattern and sound.

| Field       | Required | Description                                       |
| ----------- | -------- | ------------------------------------------------- |
| `device_id` | Yes      | The DOT that plays the animation                  |
| `preset`    | Yes      | The alert, for example `speed_trap` or `accident` |

```yaml
action: flitsmeister_dot.play_animation
data:
  device_id: your_dot_device_id
  preset: speed_trap
```

The presets cover every alert of the app: speed traps and cameras, average speed checks, traffic jams, police,
roadworks, emergency vehicles, wrong way drivers, incidents such as `accident` or `animal_on_the_road`, lane closures,
and utilities like `startup`, `fade_out` and `updating`.

### `flitsmeister_dot.play_progress`

Lights the LED ring to show how close the car is to a hazard.

| Field       | Required | Description                                                        |
| ----------- | -------- | ------------------------------------------------------------------ |
| `device_id` | Yes      | The DOT that plays the animation                                   |
| `color`     | Yes      | The color of the lit LEDs, for example `warning` or `speed_trap`   |
| `fraction`  | Yes      | How much of the ring is lit, 0 to 100 %                            |
| `blink`     | Yes      | Blink the lit LEDs and play the reduce speed sound, off by default |

```yaml
action: flitsmeister_dot.play_progress
data:
  device_id: your_dot_device_id
  color: warning
  fraction: 75
  blink: false
```

## Connection behavior

The DOT pushes its values over a live Bluetooth connection. Home Assistant does not poll it.

- **While the DOT is awake and connected**, values update the moment they change. A connected DOT stays awake, also
  while it is parked.
- **When the connection drops**, the entities turn unavailable and the integration reconnects on its own. It tries
  right away, then after 5, 10 and 30 seconds, and every 60 seconds after that, as long as Home Assistant still sees
  the DOT.
- **When the DOT sleeps**, it stops advertising and cannot be reached. It comes back on its own once it senses motion,
  which in the car happens as soon as you drive.

The DOT accepts one Bluetooth connection at a time. While Home Assistant is connected, the Flitsmeister phone app is
not.

## Diagnostic data

1. Go to **Settings** → **Devices & Services**
2. Find "Flitsmeister DOT" and open the 3 dots menu
3. Click **Download diagnostics**

The download holds the connection state, the stored volume and the last values the DOT reported. The Bluetooth address
and the serial number are redacted.

## Troubleshooting

### Setup says it cannot connect

The DOT is probably asleep. Pick it up or shake it, then try again within a minute. Check that the DOT is within
Bluetooth range of the adapter or proxy that Home Assistant uses.

### Entities stay unavailable

Wake the DOT. Each connect attempt takes up to about a minute, so give it that long. The log line
`Connecting to the DOT at ... failed, retrying` gives the reason when an attempt fails.

## Related documentation

- [Getting Started](./GETTING_STARTED.md): installation and first setup
- [Examples](./EXAMPLES.md): automation and dashboard examples
- [GitHub Issues](https://github.com/DaanVervacke/hass-flitsmeister-dot/issues): report problems
