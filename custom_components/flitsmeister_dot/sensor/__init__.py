"""Sensor platform for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from .battery import ENTITY_DESCRIPTIONS as BATTERY_DESCRIPTIONS
from .charging import ENTITY_DESCRIPTIONS as CHARGING_DESCRIPTIONS
from .entity import FlitsmeisterDotSensor
from .motion import ENTITY_DESCRIPTIONS as MOTION_DESCRIPTIONS
from .speech_language import ENTITY_DESCRIPTIONS as SPEECH_LANGUAGE_DESCRIPTIONS

PARALLEL_UPDATES = 0

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

ENTITY_DESCRIPTIONS = (
    *BATTERY_DESCRIPTIONS,
    *CHARGING_DESCRIPTIONS,
    *MOTION_DESCRIPTIONS,
    *SPEECH_LANGUAGE_DESCRIPTIONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(FlitsmeisterDotSensor(entry.runtime_data, description) for description in ENTITY_DESCRIPTIONS)
