"""Handler for the play_animation action."""

from typing import TYPE_CHECKING

import probatio

from custom_components.flitsmeister_dot.const import DOMAIN
from custom_components.flitsmeister_dot.utils import async_run_dot_write
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_get_device_and_config_entry

from .presets import PRESET_ANIMATIONS

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

PLAY_ANIMATION_SCHEMA = probatio.Schema(
    {
        probatio.Required(ATTR_DEVICE_ID): cv.string,
        probatio.Required("preset"): probatio.In(PRESET_ANIMATIONS),
    }
)


async def async_handle_play_animation(hass: HomeAssistant, call: ServiceCall) -> None:
    """Play one preset animation on the targeted DOT.

    Raises:
        HomeAssistantError: If the DOT is asleep or refused the animation.
    """
    _, entry = async_get_device_and_config_entry(hass, DOMAIN, call.data[ATTR_DEVICE_ID])
    animation = PRESET_ANIMATIONS[call.data["preset"]]()
    await async_run_dot_write(entry.runtime_data.async_play_animation(animation), "animation_failed")
