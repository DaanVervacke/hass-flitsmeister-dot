"""Battery sensor for the Flitsmeister DOT integration."""

from custom_components.flitsmeister_dot.sensor.entity import FlitsmeisterDotSensorEntityDescription
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfRatio

ENTITY_DESCRIPTIONS = (
    FlitsmeisterDotSensorEntityDescription(
        key="battery_level",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfRatio.PERCENTAGE,
        value_fn=lambda state: state.battery_level,
    ),
)
