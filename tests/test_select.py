"""Tests for the select entities."""

from typing import Any

from flitsmeister_dot_ble import Brightness, Volume
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

VOLUME = "select.flitsmeister_dot_volume"
BRIGHTNESS = "select.flitsmeister_dot_brightness"
LED_ORIENTATION = "select.flitsmeister_dot_led_orientation"


async def test_volume_write_reaches_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Changing the volume writes it to the DOT."""
    client = await wake_dot()

    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": VOLUME, "option": "low"},
        blocking=True,
    )

    assert client.written_volumes == [Volume.LOW]
    assert hass.states.get(VOLUME).state == "low"


async def test_brightness_write_reads_back(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Changing the brightness writes it and shows the read back."""
    await wake_dot()

    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": BRIGHTNESS, "option": "80"},
        blocking=True,
    )

    assert hass.states.get(BRIGHTNESS).state == "80"


async def test_led_orientation_write_reads_back(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Changing the orientation writes it and shows the read back."""
    await wake_dot()

    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": LED_ORIENTATION, "option": "upside_down"},
        blocking=True,
    )

    assert hass.states.get(LED_ORIENTATION).state == "upside_down"


async def test_brightness_options_match_the_device(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """The offered options match the device's brightness steps."""
    attributes = hass.states.get(BRIGHTNESS).attributes
    assert attributes["options"] == [str(value) for value in Brightness]


async def test_volume_options_match_the_device(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """The offered options match the device's volume levels."""
    attributes = hass.states.get(VOLUME).attributes
    assert attributes["options"] == [value.name.lower() for value in Volume]


async def test_rejected_write_raises_a_clear_error(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A write the DOT refuses raises a translated error."""
    client = await wake_dot()
    client.reject_writes = True

    with pytest.raises(HomeAssistantError, match="Failed to change the brightness"):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": BRIGHTNESS, "option": "80"},
            blocking=True,
        )


async def test_rejected_volume_write_raises_a_clear_error(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A volume write the DOT refuses raises a translated error."""
    client = await wake_dot()
    client.reject_writes = True

    with pytest.raises(HomeAssistantError, match="Failed to change the volume"):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": VOLUME, "option": "low"},
            blocking=True,
        )
