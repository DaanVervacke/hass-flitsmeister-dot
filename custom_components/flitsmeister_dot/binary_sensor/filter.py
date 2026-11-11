"""Filter maintenance binary sensor for flitsmeister_dot."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.components.binary_sensor.const import BinarySensorDeviceClass


@dataclass(frozen=True, kw_only=True)
class FlitsmeisterDotBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a binary sensor and how to read it from coordinator data."""

    value_fn: Callable[[dict[str, Any]], bool | None]


ENTITY_DESCRIPTIONS: tuple[FlitsmeisterDotBinarySensorEntityDescription, ...] = (
    FlitsmeisterDotBinarySensorEntityDescription(
        key="filter_replacement",
        translation_key="filter_replacement",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: data.get("filter_replacement"),
    ),
)


class FlitsmeisterDotFilterSensor(BinarySensorEntity, FlitsmeisterDotEntity):
    """Binary sensor reporting whether the filter needs replacing."""

    entity_description: FlitsmeisterDotBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the value read from coordinator data."""
        return self.entity_description.value_fn(self.coordinator.data)
