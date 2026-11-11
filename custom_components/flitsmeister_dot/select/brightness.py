"""Brightness select for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import Brightness

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="brightness",
        translation_key="brightness",
        options=[str(brightness) for brightness in Brightness],
    ),
)


class FlitsmeisterDotBrightnessSelect(SelectEntity, FlitsmeisterDotEntity):
    """Select entity for the LED brightness."""

    @property
    def current_option(self) -> str | None:
        """Return the brightness read back from the DOT."""
        brightness = self.coordinator.data.brightness
        return str(brightness) if brightness is not None else None

    async def async_select_option(self, option: str) -> None:
        """Write the brightness to the DOT."""
        brightness = Brightness(int(option))
        await self._async_write(
            lambda coordinator: coordinator.async_set_brightness(brightness),
            "brightness_set_failed",
        )
