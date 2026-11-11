"""Tests for the config flow."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from flitsmeister_dot_ble import DotConnectionError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .conftest import DOT_ADDRESS


def _service_info(address: str, name: str = "FM DOT") -> BluetoothServiceInfoBleak:
    return BluetoothServiceInfoBleak(
        name,
        address,
        -60,
        {},
        {},
        ["27831530-33ee-9b9c-124d-109d6b0c0a91"],
        "local",
        MagicMock(),
        MagicMock(),
        True,
        0.0,
        None,
    )


async def _start_flow(hass: HomeAssistant) -> Any:
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
    )


async def test_user_step_without_discovery_shows_manual(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """With no DOT discovered, the flow asks for the address."""
    with patch(
        "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
        return_value=[],
    ):
        result = await _start_flow(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "manual"


async def test_user_step_with_discovery_shows_menu(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """A discovered DOT offers the pick and the manual path."""
    with patch(
        "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
        return_value=[_service_info(DOT_ADDRESS)],
    ):
        result = await _start_flow(hass)

    assert result["type"] is FlowResultType.MENU
    assert result["menu_options"] == ["discovered", "manual"]


async def test_discovered_pick_creates_the_entry(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """Picking a discovered DOT validates by connecting and creates the entry."""
    with (
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
            return_value=[_service_info(DOT_ADDRESS)],
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.async_ble_device_from_address",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.FlitsmeisterDotClient"
        ) as client_cls,
    ):
        client_cls.return_value.connect = AsyncMock()
        client_cls.return_value.disconnect = AsyncMock()
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {"next_step_id": "discovered"})
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_ADDRESS: DOT_ADDRESS})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Flitsmeister DOT"
    assert result["data"] == {CONF_ADDRESS: DOT_ADDRESS}


async def test_discovered_pick_connection_failure_shows_error(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """A DOT that does not accept the connection shows the wake hint."""

    with (
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
            return_value=[_service_info(DOT_ADDRESS)],
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.async_ble_device_from_address",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.FlitsmeisterDotClient"
        ) as client_cls,
    ):
        client_cls.return_value.connect = AsyncMock(side_effect=DotConnectionError("no"))
        client_cls.return_value.disconnect = AsyncMock()
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {"next_step_id": "discovered"})
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_ADDRESS: DOT_ADDRESS})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_manual_entry_creates_the_entry(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """A typed address in lower case is validated and stored upper case."""
    with (
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
            return_value=[],
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.async_ble_device_from_address",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.FlitsmeisterDotClient"
        ) as client_cls,
    ):
        client_cls.return_value.connect = AsyncMock()
        client_cls.return_value.disconnect = AsyncMock()
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_ADDRESS: DOT_ADDRESS.lower()})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ADDRESS: DOT_ADDRESS}


async def test_manual_entry_rejects_a_malformed_address(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """An address that is not a Bluetooth address shows a field error."""
    with patch(
        "custom_components.flitsmeister_dot.config_flow_handler.config_flow.async_discovered_service_info",
        return_value=[],
    ):
        result = await _start_flow(hass)
        result = await hass.config_entries.flow.async_configure(result["flow_id"], {CONF_ADDRESS: "not-an-address"})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_ADDRESS: "invalid_address"}


async def test_bluetooth_discovery_creates_the_entry(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """The Bluetooth discovery step confirms and creates the entry."""
    with (
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.async_ble_device_from_address",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.flitsmeister_dot.config_flow_handler.validators.device.FlitsmeisterDotClient"
        ) as client_cls,
    ):
        client_cls.return_value.connect = AsyncMock()
        client_cls.return_value.disconnect = AsyncMock()
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "bluetooth"},
            data=_service_info(DOT_ADDRESS),
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "confirm"

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ADDRESS: DOT_ADDRESS}


async def test_discovery_aborts_for_a_configured_dot(
    hass: HomeAssistant,
    bluetooth: None,
) -> None:
    """A DOT that is already set up aborts the discovery flow."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Flitsmeister DOT",
        unique_id=DOT_ADDRESS,
        data={CONF_ADDRESS: DOT_ADDRESS},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "bluetooth"},
        data=_service_info(DOT_ADDRESS),
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
