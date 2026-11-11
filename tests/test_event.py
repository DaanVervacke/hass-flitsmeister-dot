"""Tests for the button event entities."""

from typing import Any

from flitsmeister_dot_ble import ButtonAction, DotButton
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.core import HomeAssistant

RED_BUTTON = "event.flitsmeister_dot_red_button"
BLUE_BUTTON = "event.flitsmeister_dot_blue_button"


async def test_short_press_fires_the_event(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A short press on the red button fires a short_press event."""
    client = await wake_dot()

    client.press(DotButton.RED, ButtonAction.SHORT_PRESS)
    await hass.async_block_till_done()

    state = hass.states.get(RED_BUTTON)
    assert state.attributes["event_type"] == "short_press"


async def test_long_press_fires_the_event(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A long press on the blue button fires a long_press event."""
    client = await wake_dot()

    client.press(DotButton.BLUE, ButtonAction.LONG_PRESS)
    await hass.async_block_till_done()

    state = hass.states.get(BLUE_BUTTON)
    assert state.attributes["event_type"] == "long_press"


async def test_held_button_does_not_fire(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A button that is held without a release fires nothing yet."""
    client = await wake_dot()

    client.press(DotButton.RED, ButtonAction.PUSHED)
    await hass.async_block_till_done()

    state = hass.states.get(RED_BUTTON)
    assert state.attributes["event_type"] is None


async def test_red_button_ignores_blue_events(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A blue button press does not fire the red button entity."""
    client = await wake_dot()

    client.press(DotButton.BLUE, ButtonAction.SHORT_PRESS)
    await hass.async_block_till_done()

    state = hass.states.get(RED_BUTTON)
    assert state.attributes["event_type"] is None
