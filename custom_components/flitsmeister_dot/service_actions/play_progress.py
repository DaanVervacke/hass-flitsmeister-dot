"""Handler for the play_progress action."""

from dataclasses import replace
from typing import TYPE_CHECKING

from flitsmeister_dot_ble import DotColor, DotError, DotNotReadyError, animations
import probatio

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_get_device_and_config_entry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

COLOR_OPTIONS = [color.name.lower() for color in DotColor]

PLAY_PROGRESS_SCHEMA = probatio.Schema(
    {
        probatio.Required(ATTR_DEVICE_ID): cv.string,
        probatio.Required("color"): probatio.In(COLOR_OPTIONS),
        probatio.Required("fraction"): probatio.All(int, probatio.Range(min=0, max=100)),
        probatio.Optional("blink", default=False): cv.boolean,
    }
)


async def async_handle_play_progress(hass: HomeAssistant, call: ServiceCall) -> None:
    """Play the approach progress animation on the targeted DOT.

    Raises:
        HomeAssistantError: If the DOT is asleep or refused the animation.
    """
    _, entry = async_get_device_and_config_entry(hass, DOMAIN, call.data[ATTR_DEVICE_ID])
    color = DotColor[call.data["color"].upper()]
    fraction = call.data["fraction"] / 100
    animation = (
        replace(animations.overspeed(fraction=fraction), color=color)
        if call.data["blink"]
        else animations.progress(color=color, fraction=fraction)
    )
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
