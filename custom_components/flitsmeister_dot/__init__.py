"""The Flitsmeister DOT integration."""

from custom_components.flitsmeister_dot.const import DOMAIN
from custom_components.flitsmeister_dot.coordinator import FlitsmeisterDotCoordinator
from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
from custom_components.flitsmeister_dot.service_actions import async_setup_services
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

PLATFORMS = [Platform.EVENT, Platform.SELECT, Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the service actions.

    Returns:
        True once the actions are registered.
    """
    async_setup_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
) -> bool:
    """Set up one DOT from its config entry.

    Returns:
        True once every platform is forwarded and the coordinator
        listens for the DOT to wake.
    """
    coordinator = FlitsmeisterDotCoordinator(hass, entry)
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(coordinator.async_stop)
    coordinator.async_start()
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
) -> bool:
    """Unload one DOT.

    Returns:
        True if every platform unloaded cleanly.
    """
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
