"""Charging sensor for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import ChargingState

from custom_components.flitsmeister_dot.sensor.entity import FlitsmeisterDotSensorEntityDescription
from homeassistant.components.sensor import SensorDeviceClass

CHARGING_STATES = {
    ChargingState.CONSUMING: "unplugged",
    ChargingState.CHARGING: "charging",
    ChargingState.CHARGING_DONE: "plugged_in",
}

ENTITY_DESCRIPTIONS = (
    FlitsmeisterDotSensorEntityDescription(
        key="charging_state",
        translation_key="charging_state",
        device_class=SensorDeviceClass.ENUM,
        options=list(CHARGING_STATES.values()),
        value_fn=lambda state: CHARGING_STATES[state.charging_state] if state.charging_state is not None else None,
    ),
)
