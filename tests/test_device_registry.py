"""Tests for config-entry-scoped device ownership."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .conftest import DOT_ADDRESS, FakeBluetooth, FakeDots


async def test_entry_owns_its_own_device(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
) -> None:
    """A loaded entry registers exactly one device, owned by that entry."""
    devices = dr.async_entries_for_config_entry(dr.async_get(hass), init_integration.entry_id)

    assert len(devices) == 1
    assert devices[0].config_entry_id == init_integration.entry_id


async def test_two_entries_get_separate_devices(
    hass: HomeAssistant,
    mock_dot: FakeDots,
    mock_bluetooth: FakeBluetooth,
    init_integration: MockConfigEntry,
) -> None:
    """Two DOTs never share a device, and entry-scoped lookups keep them apart."""

    second_address = "11:22:33:44:55:66"
    second_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Flitsmeister DOT",
        unique_id=second_address,
        data={CONF_ADDRESS: second_address},
    )
    second_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(second_entry.entry_id)
    await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    first_device = device_registry.async_get_device_by_identifier(
        (DOMAIN, DOT_ADDRESS),
        init_integration.entry_id,
    )
    second_device = device_registry.async_get_device_by_identifier(
        (DOMAIN, second_address),
        second_entry.entry_id,
    )

    assert first_device is not None
    assert second_device is not None
    assert first_device.id != second_device.id
