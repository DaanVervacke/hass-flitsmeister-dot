"""Select platform for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from .brightness import ENTITY_DESCRIPTIONS as BRIGHTNESS_DESCRIPTIONS, FlitsmeisterDotBrightnessSelect
from .led_orientation import ENTITY_DESCRIPTIONS as LED_ORIENTATION_DESCRIPTIONS, FlitsmeisterDotLedOrientationSelect
from .volume import ENTITY_DESCRIPTIONS as VOLUME_DESCRIPTIONS, FlitsmeisterDotVolumeSelect

PARALLEL_UPDATES = 1

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator = entry.runtime_data
    async_add_entities(FlitsmeisterDotVolumeSelect(coordinator, description) for description in VOLUME_DESCRIPTIONS)
    async_add_entities(
        FlitsmeisterDotBrightnessSelect(coordinator, description) for description in BRIGHTNESS_DESCRIPTIONS
    )
    async_add_entities(
        FlitsmeisterDotLedOrientationSelect(coordinator, description) for description in LED_ORIENTATION_DESCRIPTIONS
    )
