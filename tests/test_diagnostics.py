"""Tests for the diagnostics output."""

from typing import Any

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry

from homeassistant.core import HomeAssistant

from .conftest import DOT_ADDRESS

TO_REDACT = [
    DOT_ADDRESS,
    "0011223344556677",
    "AABBCCDD-1122-3344-5566-77889900AABB",
]


async def test_diagnostics_redact_the_identity(
    init_integration: MockConfigEntry,
    hass: HomeAssistant,
    hass_client: Any,
    wake_dot: Any,
) -> None:
    """The diagnostics never contain the address or the serial."""
    await wake_dot()

    result = await get_diagnostics_for_config_entry(hass, hass_client, init_integration)

    dumped = str(result)
    for value in TO_REDACT:
        assert value not in dumped
    assert result["coordinator"]["data"]["battery_level"] == 80
