"""Handler for the play_animation action."""

from typing import TYPE_CHECKING

from flitsmeister_dot_ble import DotError, DotNotReadyError
import probatio

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError
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
    try:
        await entry.runtime_data.async_play_animation(animation)
    except DotNotReadyError as exception:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="device_asleep",
        ) from exception
    except DotError as exception:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="animation_failed",
        ) from exception
