"""Tests for the integration setup and the session lifecycle."""

import asyncio
from typing import Any

from flitsmeister_dot_ble import Volume, animations
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, mock_restore_cache

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_ADDRESS, STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import device_registry as dr

from .conftest import DOT_ADDRESS, FakeBluetooth, FakeDots

ENTITY_IDS = [
    "sensor.flitsmeister_dot_battery",
    "sensor.flitsmeister_dot_charging",
    "sensor.flitsmeister_dot_motion",
    "sensor.flitsmeister_dot_speech_language",
    "select.flitsmeister_dot_volume",
    "select.flitsmeister_dot_brightness",
    "select.flitsmeister_dot_led_orientation",
    "event.flitsmeister_dot_red_button",
    "event.flitsmeister_dot_blue_button",
]


async def test_entities_exist_and_wait_for_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """Setup succeeds with the DOT asleep and every entity is unavailable."""
    assert init_integration.state is ConfigEntryState.LOADED
    for entity_id in ENTITY_IDS:
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == STATE_UNAVAILABLE


async def test_waking_the_dot_fills_every_entity(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """One advertisement connects the DOT and pushes its values."""
    await wake_dot()

    assert hass.states.get("sensor.flitsmeister_dot_battery").state == "80"
    assert hass.states.get("sensor.flitsmeister_dot_charging").state == "unplugged"
    assert hass.states.get("sensor.flitsmeister_dot_motion").state == "parked"
    assert hass.states.get("sensor.flitsmeister_dot_speech_language").state == "dutch"
    assert hass.states.get("select.flitsmeister_dot_brightness").state == "50"
    assert hass.states.get("select.flitsmeister_dot_led_orientation").state == "normal"


async def test_session_start_plays_the_startup_animation(
    init_integration: MockConfigEntry,
    wake_dot: Any,
) -> None:
    """The connect sequence plays the startup animation."""
    client = await wake_dot()

    assert client.played_animations[0] == animations.startup()


async def test_restored_volume_is_written_on_connect(
    hass: HomeAssistant,
    bluetooth: None,
    mock_dot: FakeDots,
    mock_bluetooth: FakeBluetooth,
) -> None:
    """The volume restored by the entity reaches the DOT on the next connect."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Flitsmeister DOT",
        unique_id=DOT_ADDRESS,
        data={CONF_ADDRESS: DOT_ADDRESS},
    )
    entry.add_to_hass(hass)
    mock_restore_cache(
        hass,
        [
            State(
                "select.flitsmeister_dot_volume",
                "normal",
                attributes={"options": ["silent", "low", "normal", "hard"]},
            )
        ],
    )
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    mock_bluetooth.advertise()
    await hass.async_block_till_done(wait_background_tasks=True)

    client = mock_dot[-1]
    assert client.written_volumes == [Volume.NORMAL]


async def test_sleeping_dot_makes_entities_unavailable(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_bluetooth: FakeBluetooth,
    wake_dot: Any,
) -> None:
    """A lost session with the DOT out of reach marks every entity unavailable."""
    client = await wake_dot()
    assert hass.states.get("sensor.flitsmeister_dot_battery").state == "80"

    mock_bluetooth.present = False
    client.drop_connection()
    await hass.async_block_till_done()

    assert hass.states.get("sensor.flitsmeister_dot_battery").state == STATE_UNAVAILABLE


async def test_advertisement_reconnects_a_dot_that_was_out_of_reach(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_bluetooth: FakeBluetooth,
    wake_dot: Any,
) -> None:
    """A DOT that left and came back connects on its next advertisement."""
    first_client = await wake_dot()
    mock_bluetooth.present = False
    first_client.drop_connection()
    await hass.async_block_till_done()

    second_client = await wake_dot()
    assert second_client is not first_client
    assert hass.states.get("sensor.flitsmeister_dot_battery").state == "80"


async def test_device_info_comes_from_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """The device registry entry fills in with the values read from the DOT."""
    await wake_dot()

    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, DOT_ADDRESS), init_integration.entry_id)
    assert device is not None
    assert device.manufacturer == "Flitsmeister"
    assert device.model == "DOT"
    assert device.sw_version == "2.9.0"
    assert device.serial_number == "AABBCCDD-1122-3344-5566-77889900AABB"


async def test_unload_disconnects_the_dot(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """Unloading the entry disconnects the session."""
    client = await wake_dot()

    await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert init_integration.state is ConfigEntryState.NOT_LOADED
    assert client.connected is False


async def test_lost_session_reconnects_without_an_advertisement(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_dot: FakeDots,
    wake_dot: Any,
) -> None:
    """A dropped link reconnects on its own while the DOT stays in reach."""
    first_client = await wake_dot()

    first_client.drop_connection()
    await hass.async_block_till_done(wait_background_tasks=True)

    assert len(mock_dot) == 2
    assert mock_dot[-1].connected is True
    assert hass.states.get("sensor.flitsmeister_dot_battery").state == "80"


async def test_failed_connects_are_retried(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_dot: FakeDots,
    wake_dot: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Failed connects retry until the DOT answers, with one warning."""
    mock_dot.failures_to_inject = 2

    await wake_dot()

    assert len(mock_dot) == 3
    assert mock_dot[-1].connected is True
    assert hass.states.get("sensor.flitsmeister_dot_battery").state == "80"
    warnings = [record for record in caplog.records if "failed, retrying" in record.getMessage()]
    assert len(warnings) == 1
    assert "The DOT did not answer" in warnings[0].getMessage()
    assert "Reconnected to the DOT" in caplog.text


async def test_unload_cancels_a_running_connect(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    mock_dot: FakeDots,
    mock_bluetooth: FakeBluetooth,
) -> None:
    """Unloading while a connect is still running stops it cleanly."""
    mock_dot.connect_gate = asyncio.Event()
    mock_bluetooth.advertise()
    await hass.async_block_till_done(wait_background_tasks=False)
    assert len(mock_dot) == 1

    await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()

    assert init_integration.state is ConfigEntryState.NOT_LOADED
    assert mock_dot[0].connected is False


async def test_unchanged_values_do_not_rewrite_states(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    wake_dot: Any,
) -> None:
    """A notification that changes nothing leaves every state untouched."""
    client = await wake_dot()
    before = hass.states.get("sensor.flitsmeister_dot_battery").last_updated

    client.emit_state()
    await hass.async_block_till_done()

    assert hass.states.get("sensor.flitsmeister_dot_battery").last_updated == before
