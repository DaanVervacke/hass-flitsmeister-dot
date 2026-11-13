"""Handler for the play_progress action."""

from collections.abc import Mapping
from dataclasses import replace
from typing import TYPE_CHECKING, Any

from flitsmeister_dot_ble import DotColor, DotSound, animations
import probatio

from custom_components.flitsmeister_dot.const import DOMAIN
from custom_components.flitsmeister_dot.utils import async_run_dot_write
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_get_device_and_config_entry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant, ServiceCall

ATTR_COLOR = "color"
ATTR_RGB_COLOR = "rgb_color"
ATTR_SOUND = "sound"
COLOR_OPTIONS = [color.name.lower() for color in DotColor]
SOUND_PREFIX = "SFX_"
SOUND_OPTIONS = {
    sound.name.removeprefix(SOUND_PREFIX).lower(): sound for sound in DotSound if sound.name.startswith(SOUND_PREFIX)
}
OPAQUE_ALPHA = 0xFF000000

PLAY_PROGRESS_SCHEMA = probatio.All(
    probatio.Schema(
        {
            probatio.Required(ATTR_DEVICE_ID): cv.string,
            probatio.Exclusive(ATTR_COLOR, "color_source"): probatio.In(COLOR_OPTIONS),
            probatio.Exclusive(ATTR_RGB_COLOR, "color_source"): probatio.All(
                probatio.ExactSequence((cv.byte, cv.byte, cv.byte)), probatio.Coerce(tuple)
            ),
            probatio.Required("fraction"): probatio.All(int, probatio.Range(min=0, max=100)),
            probatio.Optional("blink", default=False): cv.boolean,
            probatio.Optional(ATTR_SOUND): probatio.In(SOUND_OPTIONS),
        }
    ),
    cv.has_at_least_one_key(ATTR_COLOR, ATTR_RGB_COLOR),
)


def _argb(red: int, green: int, blue: int) -> int:
    """Return the opaque ARGB int the DOT expects for an RGB color."""
    return OPAQUE_ALPHA | red << 16 | green << 8 | blue


def _color(data: Mapping[str, Any]) -> int:
    """Return the color from the named color or the RGB color of the call."""
    if ATTR_RGB_COLOR in data:
        return _argb(*data[ATTR_RGB_COLOR])
    return DotColor[data[ATTR_COLOR].upper()]


async def async_handle_play_progress(hass: HomeAssistant, call: ServiceCall) -> None:
    """Play the approach progress animation on the targeted DOT.

    Raises:
        HomeAssistantError: If the DOT is asleep or refused the animation.
    """
    _, entry = async_get_device_and_config_entry(hass, DOMAIN, call.data[ATTR_DEVICE_ID])
    color = _color(call.data)
    fraction = call.data["fraction"] / 100
    animation = (
        replace(animations.overspeed(fraction=fraction), color=color)
        if call.data["blink"]
        else animations.progress(color=color, fraction=fraction)
    )
    if ATTR_SOUND in call.data:
        animation = replace(animation, primary_sound=SOUND_OPTIONS[call.data[ATTR_SOUND]])
    await async_run_dot_write(entry.runtime_data.async_play_animation(animation), "animation_failed")
