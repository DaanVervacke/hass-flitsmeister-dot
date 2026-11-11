"""probatio schemas for the config flow forms."""

from typing import Any

import probatio

from homeassistant.const import CONF_ADDRESS


def get_manual_schema(user_input: dict[str, Any] | None) -> probatio.Schema:
    """Return the form that asks for the Bluetooth address."""
    return probatio.Schema(
        {
            probatio.Required(
                CONF_ADDRESS,
                default=(user_input or {}).get(CONF_ADDRESS, ""),
            ): str,
        }
    )


def get_discovered_schema(
    dots: dict[str, str],
    current_address: str | None,
) -> probatio.Schema:
    """Return the form that picks one of the discovered DOTs.

    Args:
        dots: The Bluetooth address of every discovered DOT, mapped to
            its label in the dropdown.
        current_address: The address chosen in a previous attempt.
    """
    return probatio.Schema(
        {
            probatio.Required(
                CONF_ADDRESS,
                default=current_address or next(iter(dots)),
            ): probatio.In(dots),
        }
    )
