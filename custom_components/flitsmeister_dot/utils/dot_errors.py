"""Turn DOT library errors into the errors Home Assistant shows to users."""

from collections.abc import Awaitable

from flitsmeister_dot_ble import DotError, DotNotReadyError

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.exceptions import HomeAssistantError


async def async_run_dot_write(write: Awaitable[None], translation_key: str) -> None:
    """Await one write to the DOT and raise a translated error when it fails.

    Args:
        write: The pending write to the DOT.
        translation_key: Key of the message shown when the DOT refuses the write.

    Raises:
        HomeAssistantError: If the DOT is asleep or refused the write.
    """
    try:
        await write
    except DotNotReadyError as exception:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="device_asleep",
        ) from exception
    except DotError as exception:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key=translation_key,
        ) from exception
