"""Base entity class for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from custom_components.flitsmeister_dot.const import DEVICE_NAME, DOMAIN
from custom_components.flitsmeister_dot.coordinator import FlitsmeisterDotCoordinator
from custom_components.flitsmeister_dot.utils import async_run_dot_write
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.helpers.entity import EntityDescription


class FlitsmeisterDotEntity(CoordinatorEntity[FlitsmeisterDotCoordinator]):
    """Base entity with the device info and the write error handling."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FlitsmeisterDotCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        address = coordinator.config_entry.data[CONF_ADDRESS]
        self._attr_unique_id = f"{address}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=DEVICE_NAME,
        )

    async def _async_write(
        self,
        call: Callable[[FlitsmeisterDotCoordinator], Awaitable[None]],
        translation_key: str,
    ) -> None:
        """Run one write against the DOT and turn its failures into user errors.

        Args:
            call: Receives the coordinator and performs the write.
            translation_key: Key of the message shown when the write fails.
        """
        await async_run_dot_write(call(self.coordinator), translation_key)
