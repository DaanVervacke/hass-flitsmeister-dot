# Usage Examples

Automation and dashboard examples for the Flitsmeister DOT integration. Replace `your_dot_device_id` with the device
ID of your DOT. The automation editor fills it in for you when you pick the DOT as the target device.

## Button automations

The red and blue buttons are event entities. Every press fires `short_press` or `long_press` in the `event_type`
attribute. A press shorter than one second is a short press.

### Toggle a light with the blue button

```yaml
automation:
  - alias: "DOT blue button toggles the garage light"
    trigger:
      - trigger: state
        entity_id: event.flitsmeister_dot_blue_button
    condition:
      - condition: state
        entity_id: event.flitsmeister_dot_blue_button
        attribute: event_type
        state: short_press
    action:
      - action: light.toggle
        target:
          entity_id: light.garage
```

### Different actions for short and long presses

```yaml
automation:
  - alias: "DOT red button"
    trigger:
      - trigger: state
        entity_id: event.flitsmeister_dot_red_button
    action:
      - choose:
          - conditions:
              - condition: state
                entity_id: event.flitsmeister_dot_red_button
                attribute: event_type
                state: short_press
            sequence:
              - action: cover.open_cover
                target:
                  entity_id: cover.garage_door
          - conditions:
              - condition: state
                entity_id: event.flitsmeister_dot_red_button
                attribute: event_type
                state: long_press
            sequence:
              - action: cover.close_cover
                target:
                  entity_id: cover.garage_door
```

## Alerts on the DOT

### Warn when the garage door is left open

```yaml
automation:
  - alias: "DOT warns about an open garage door"
    trigger:
      - trigger: state
        entity_id: sensor.flitsmeister_dot_motion
        to: driving
    condition:
      - condition: state
        entity_id: cover.garage_door
        state: open
    action:
      - action: flitsmeister_dot.play_animation
        data:
          device_id: your_dot_device_id
          preset: dangerous_situation
```

### Show a countdown on the LED ring

Fill the ring as a timer runs out, and blink it for the last quarter:

```yaml
script:
  dot_countdown:
    sequence:
      - repeat:
          for_each: [25, 50, 75]
          sequence:
            - action: flitsmeister_dot.play_progress
              data:
                device_id: your_dot_device_id
                color: success
                fraction: "{{ repeat.item }}"
                blink: false
            - delay: "00:01:00"
      - action: flitsmeister_dot.play_progress
        data:
          device_id: your_dot_device_id
          color: warning
          fraction: 100
          blink: true
```

## Battery and charging

### Notify when the battery runs low

```yaml
automation:
  - alias: "DOT battery low"
    trigger:
      - trigger: numeric_state
        entity_id: sensor.flitsmeister_dot_battery
        below: 15
    condition:
      - condition: state
        entity_id: sensor.flitsmeister_dot_charging
        state: unplugged
    action:
      - action: notify.notify
        data:
          message: "The DOT battery is at {{ states('sensor.flitsmeister_dot_battery') }} %."
```

## Dashboard

```yaml
type: vertical-stack
cards:
  - type: glance
    title: Flitsmeister DOT
    entities:
      - entity: sensor.flitsmeister_dot_battery
        name: Battery
      - entity: sensor.flitsmeister_dot_charging
        name: Charging
      - entity: sensor.flitsmeister_dot_motion
        name: Motion
  - type: entities
    entities:
      - select.flitsmeister_dot_volume
      - select.flitsmeister_dot_brightness
      - select.flitsmeister_dot_led_orientation
```

## Tips

- An action sent while the DOT sleeps fails with a clear error. Add `continue_on_error: true` to the action in an
  automation that may run while the car is parked.
- The motion sensor only changes while the DOT is connected. A DOT that wakes up in a parked car connects first and
  then reports `driving`, which takes up to about a minute.
