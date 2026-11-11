"""Repairs platform for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create the repair flow for an issue this integration raised.

    Returns:
        The flow that fixes the issue.
    """
    return ConfirmRepairFlow()
