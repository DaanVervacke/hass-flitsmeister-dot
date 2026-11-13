"""Tests for the play_animation and play_progress actions."""

from typing import Any

from flitsmeister_dot_ble import DotAnimationType, DotColor, DotSound, animations
import probatio
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from .conftest import DOT_ADDRESS


async def _device_id(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, DOT_ADDRESS), entry.entry_id)
    assert device is not None
    return device.id


async def test_play_animation_reaches_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """The chosen preset is played on the DOT."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_animation",
        {
            "device_id": await _device_id(hass, init_integration),
            "preset": "speed_trap",
        },
        blocking=True,
    )

    assert client.played_animations[-1] == animations.speed_trap()


async def test_play_animation_while_asleep_raises(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Playing an animation on a sleeping DOT raises a clear error."""
    with pytest.raises(HomeAssistantError, match="asleep"):
        await hass.services.async_call(
            DOMAIN,
            "play_animation",
            {
                "device_id": await _device_id(hass, init_integration),
                "preset": "speed_trap",
            },
            blocking=True,
        )


async def test_play_progress_reaches_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """The progress animation is played with the chosen color and fraction."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_progress",
        {
            "device_id": await _device_id(hass, init_integration),
            "color": "speed_trap",
            "fraction": 50,
        },
        blocking=True,
    )

    assert client.played_animations[-1] == animations.progress(color=DotColor.SPEED_TRAP, fraction=0.5)


async def test_play_progress_blink_overspeed(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """The blink option plays the overspeed animation."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_progress",
        {
            "device_id": await _device_id(hass, init_integration),
            "color": "danger",
            "fraction": 75,
            "blink": True,
        },
        blocking=True,
    )

    assert client.played_animations[-1] == animations.overspeed(fraction=0.75)


async def test_play_progress_blink_keeps_the_chosen_color(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Blinking uses the chosen color instead of the overspeed red."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_progress",
        {
            "device_id": await _device_id(hass, init_integration),
            "color": "speed_cam",
            "fraction": 50,
            "blink": True,
        },
        blocking=True,
    )

    played = client.played_animations[-1]
    assert played.type is DotAnimationType.PROGRESSION_BLINK
    assert played.color == DotColor.SPEED_CAM
    assert played.primary_sound is DotSound.SFX_REDUCE_SPEED


async def test_play_progress_rgb_color(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """An RGB color reaches the DOT as an opaque ARGB color."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_progress",
        {
            "device_id": await _device_id(hass, init_integration),
            "rgb_color": [255, 85, 0],
            "fraction": 50,
        },
        blocking=True,
    )

    assert client.played_animations[-1] == animations.progress(color=0xFFFF5500, fraction=0.5)


async def test_play_progress_rgb_color_blink(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Blinking keeps the RGB color."""
    client = await wake_dot()

    await hass.services.async_call(
        DOMAIN,
        "play_progress",
        {
            "device_id": await _device_id(hass, init_integration),
            "rgb_color": [0, 255, 0],
            "fraction": 25,
            "blink": True,
        },
        blocking=True,
    )

    played = client.played_animations[-1]
    assert played.type is DotAnimationType.PROGRESSION_BLINK
    assert played.color == 0xFF00FF00


@pytest.mark.parametrize(
    "colors",
    [
        pytest.param({}, id="no_color"),
        pytest.param({"color": "danger", "rgb_color": [255, 0, 0]}, id="both_colors"),
        pytest.param({"rgb_color": [255, 0]}, id="two_channels"),
        pytest.param({"rgb_color": [256, 0, 0]}, id="channel_out_of_range"),
    ],
)
async def test_play_progress_rejects_invalid_color(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    colors: dict[str, Any],
) -> None:
    """The action needs exactly one valid color."""
    with pytest.raises(probatio.Invalid):
        await hass.services.async_call(
            DOMAIN,
            "play_progress",
            {"device_id": await _device_id(hass, init_integration), "fraction": 50, **colors},
            blocking=True,
        )
