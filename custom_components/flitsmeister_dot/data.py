"""Runtime data type for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.coordinator import FlitsmeisterDotCoordinator
    from homeassistant.config_entries import ConfigEntry

type FlitsmeisterDotConfigEntry = ConfigEntry[FlitsmeisterDotCoordinator]
