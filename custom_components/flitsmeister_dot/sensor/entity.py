"""Sensor entity for the Flitsmeister DOT integration."""

from collections.abc import Callable
from dataclasses import dataclass

from flitsmeister_dot_ble import DotState

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class FlitsmeisterDotSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from the DOT state."""

    value_fn: Callable[[DotState], StateType]


class FlitsmeisterDotSensor(SensorEntity, FlitsmeisterDotEntity):
    """Sensor backed by one value in the DOT state."""

    entity_description: FlitsmeisterDotSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value read from the DOT state."""
        return self.entity_description.value_fn(self.coordinator.data)
