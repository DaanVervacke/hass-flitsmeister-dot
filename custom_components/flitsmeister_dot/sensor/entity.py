"""Sensor entity for flitsmeister_dot."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True, kw_only=True)
class FlitsmeisterDotSensorEntityDescription(SensorEntityDescription):
    """Describes a sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict[str, Any]], StateType]


class FlitsmeisterDotSensor(SensorEntity, FlitsmeisterDotEntity):
    """Sensor backed by one value in the coordinator payload."""

    entity_description: FlitsmeisterDotSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
