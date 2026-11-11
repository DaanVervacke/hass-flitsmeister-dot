"""Event platform for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from .button import BUTTON_BY_KEY, ENTITY_DESCRIPTIONS, FlitsmeisterDotButtonEvent

PARALLEL_UPDATES = 0

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the event platform."""
    async_add_entities(
        FlitsmeisterDotButtonEvent(entry.runtime_data, description, BUTTON_BY_KEY[description.key])
        for description in ENTITY_DESCRIPTIONS
    )
