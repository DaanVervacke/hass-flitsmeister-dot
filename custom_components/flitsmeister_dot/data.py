"""
Runtime data types for flitsmeister_dot.

Access pattern: entry.runtime_data.client / entry.runtime_data.coordinator
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import FlitsmeisterDotApiClient
    from .coordinator import FlitsmeisterDotDataUpdateCoordinator


type FlitsmeisterDotConfigEntry = ConfigEntry[FlitsmeisterDotData]


@dataclass
class FlitsmeisterDotData:
    """Runtime data stored on the config entry after a successful setup."""

    client: FlitsmeisterDotApiClient
    coordinator: FlitsmeisterDotDataUpdateCoordinator
    integration: Integration
