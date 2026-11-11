"""Validation for the Bluetooth address of a DOT."""

import re

from flitsmeister_dot_ble import BleakTransport, DotError, FlitsmeisterDotClient

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant

BLE_ADDRESS_PATTERN = re.compile(r"^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$")


class FlitsmeisterDotAddressError(Exception):
    """The address is not a Bluetooth address."""


class FlitsmeisterDotConnectError(Exception):
    """The DOT did not accept a connection."""


def validate_address_format(address: str) -> None:
    """Raise FlitsmeisterDotAddressError when the address is malformed.

    Args:
        address: The address the user entered.
    """
    if BLE_ADDRESS_PATTERN.match(address) is None:
        raise FlitsmeisterDotAddressError(address)


async def validate_connection(hass: HomeAssistant, address: str) -> None:
    """Connect to the DOT once to prove the address reaches a device.

    Args:
        hass: The Home Assistant instance that knows the Bluetooth adapters.
        address: The Bluetooth address of the DOT.

    Raises:
        FlitsmeisterDotConnectError: The Bluetooth integration does not
            know the address or the DOT did not accept the connection.
    """
    device = async_ble_device_from_address(hass, address, connectable=True)
    if device is None:
        raise FlitsmeisterDotConnectError(address)
    client = FlitsmeisterDotClient(BleakTransport(device))
    try:
        await client.connect()
    except DotError as exception:
        raise FlitsmeisterDotConnectError(address) from exception
    finally:
        await client.disconnect()
