"""Motion sensor for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import MotionStatus

from custom_components.flitsmeister_dot.sensor.entity import FlitsmeisterDotSensorEntityDescription
from homeassistant.components.sensor import SensorDeviceClass

MOTION_OPTIONS = [status.name.lower() for status in MotionStatus]

ENTITY_DESCRIPTIONS = (
    FlitsmeisterDotSensorEntityDescription(
        key="motion_status",
        translation_key="motion_status",
        device_class=SensorDeviceClass.ENUM,
        options=MOTION_OPTIONS,
        value_fn=lambda state: state.motion_status.name.lower() if state.motion_status is not None else None,
    ),
)
