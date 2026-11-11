"""Diagnostics support for the Flitsmeister DOT integration."""

from dataclasses import asdict, fields
from enum import Enum
from typing import TYPE_CHECKING, Any

from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.redact import async_redact_data

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
    from homeassistant.core import HomeAssistant

TO_REDACT = {CONF_ADDRESS, "serial_raw", "serial_uuid"}


def _state_record(state: Any) -> dict[str, Any] | None:
    """Return the DOT state as a plain dict with enum names instead of values."""
    if state is None:
        return None
    record = asdict(state)
    for field in fields(state):
        value = getattr(state, field.name)
        if isinstance(value, Enum):
            record[field.name] = value.name.lower()
    return record


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: FlitsmeisterDotConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry.

    Returns:
        The redacted entry configuration and the current DOT state.
    """
    coordinator = entry.runtime_data
    return {
        "entry": {
            "version": entry.version,
            "minor_version": entry.minor_version,
            "state": str(entry.state),
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
            "volume": coordinator.volume.name.lower() if coordinator.volume is not None else None,
            "data": async_redact_data(_state_record(coordinator.data), TO_REDACT),
        },
    }
