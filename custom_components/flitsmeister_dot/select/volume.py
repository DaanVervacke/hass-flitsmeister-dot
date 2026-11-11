"""Volume select for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import Volume

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.restore_state import RestoreEntity

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="volume",
        translation_key="volume",
        options=[volume.name.lower() for volume in Volume],
    ),
)


class FlitsmeisterDotVolumeSelect(RestoreEntity, SelectEntity, FlitsmeisterDotEntity):
    """Select entity for the speaker volume."""

    async def async_added_to_hass(self) -> None:
        """Adopt the volume restored from the previous run."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.state in self.options:
            self.coordinator.async_restore_volume(Volume[last_state.state.upper()])

    @property
    def current_option(self) -> str | None:
        """Return the volume written to the DOT on connect."""
        volume = self.coordinator.volume
        return volume.name.lower() if volume is not None else None

    async def async_select_option(self, option: str) -> None:
        """Store the volume and write it to the DOT when it is connected."""
        volume = Volume[option.upper()]
        await self._async_write(
            lambda coordinator: coordinator.async_set_volume(volume),
            "volume_set_failed",
        )
