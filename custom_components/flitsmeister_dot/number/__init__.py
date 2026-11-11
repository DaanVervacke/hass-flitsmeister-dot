"""Number platform for flitsmeister_dot."""

from typing import TYPE_CHECKING

from .target_humidity import ENTITY_DESCRIPTIONS, FlitsmeisterDotHumidityNumber

# Acts on the device: the coordinator does not limit outbound calls.
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
    """Set up the number platform."""
    async_add_entities(
        FlitsmeisterDotHumidityNumber(entry.runtime_data.coordinator, description)
        for description in ENTITY_DESCRIPTIONS
    )
