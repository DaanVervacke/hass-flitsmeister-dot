"""LED orientation select for the Flitsmeister DOT integration."""

from flitsmeister_dot_ble import LedOrientation

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription

ENTITY_DESCRIPTIONS = (
    SelectEntityDescription(
        key="led_orientation",
        translation_key="led_orientation",
        options=[orientation.name.lower() for orientation in LedOrientation],
    ),
)


class FlitsmeisterDotLedOrientationSelect(SelectEntity, FlitsmeisterDotEntity):
    """Select entity for the LED ring orientation."""

    @property
    def current_option(self) -> str | None:
        """Return the orientation read back from the DOT."""
        orientation = self.coordinator.data.led_orientation
        return orientation.name.lower() if orientation is not None else None

    async def async_select_option(self, option: str) -> None:
        """Write the orientation to the DOT."""
        orientation = LedOrientation[option.upper()]
        await self._async_write(
            lambda coordinator: coordinator.async_set_led_orientation(orientation),
            "led_orientation_set_failed",
        )
