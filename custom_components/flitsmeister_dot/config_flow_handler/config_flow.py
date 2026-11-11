"""Config flow for the Flitsmeister DOT integration."""

from typing import Any

from flitsmeister_dot_ble import is_dot_advertisement

from custom_components.flitsmeister_dot.const import DEVICE_NAME, DOMAIN, LOGGER
from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak, async_discovered_service_info
from homeassistant.const import CONF_ADDRESS

from .schemas import get_discovered_schema, get_manual_schema
from .validators import (
    FlitsmeisterDotAddressError,
    FlitsmeisterDotConnectError,
    validate_address_format,
    validate_connection,
)


class FlitsmeisterDotConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for the Flitsmeister DOT integration."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow without a chosen address."""
        self._address: str | None = None

    async def async_step_bluetooth(
        self,
        discovery_info: BluetoothServiceInfoBleak,
    ) -> config_entries.ConfigFlowResult:
        """Handle a DOT discovered through its advertisements."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._address = discovery_info.address
        self.context["title_placeholders"] = {"name": DEVICE_NAME}
        return await self.async_step_confirm()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Let the user pick a discovered DOT or enter an address.

        Returns:
            The menu, or the manual address form.
        """
        if self._async_discovered_dots():
            return self.async_show_menu(
                step_id="user",
                menu_options=["discovered", "manual"],
            )
        return await self.async_step_manual()

    async def async_step_discovered(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the user picking one of the discovered DOTs.

        Returns:
            The form, or the created config entry.
        """
        errors: dict[str, str] = {}
        dots = self._async_discovered_dots()
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            try:
                await validate_connection(self.hass, address)
            except FlitsmeisterDotConnectError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - Anything unexpected still has to reach the form.
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=DEVICE_NAME,
                    data={CONF_ADDRESS: address},
                )
        return self.async_show_form(
            step_id="discovered",
            data_schema=get_discovered_schema(dots, self._address),
            errors=errors,
        )

    async def async_step_manual(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the user typing the Bluetooth address.

        Returns:
            The form, or the created config entry.
        """
        errors: dict[str, str] = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            try:
                validate_address_format(address)
            except FlitsmeisterDotAddressError:
                errors[CONF_ADDRESS] = "invalid_address"
            else:
                await self.async_set_unique_id(address.upper())
                self._abort_if_unique_id_configured()
                try:
                    await validate_connection(self.hass, address.upper())
                except FlitsmeisterDotConnectError:
                    errors["base"] = "cannot_connect"
                except Exception:  # noqa: BLE001 - Anything unexpected still has to reach the form.
                    LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title=DEVICE_NAME,
                        data={CONF_ADDRESS: address.upper()},
                    )
        return self.async_show_form(
            step_id="manual",
            data_schema=get_manual_schema(user_input),
            errors=errors,
        )

    async def async_step_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Confirm the DOT found through discovery.

        Returns:
            The form, or the created config entry.
        """
        errors: dict[str, str] = {}
        address = self._address
        if user_input is not None and address is not None:
            try:
                await validate_connection(self.hass, address)
            except FlitsmeisterDotConnectError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001 - Anything unexpected still has to reach the form.
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=DEVICE_NAME,
                    data={CONF_ADDRESS: address},
                )
        return self.async_show_form(step_id="confirm", errors=errors)

    def _async_discovered_dots(self) -> dict[str, str]:
        """Return the address and label of every discovered DOT."""
        known = {entry.unique_id for entry in self._async_current_entries() if entry.unique_id is not None}
        dots: dict[str, str] = {}
        for service_info in async_discovered_service_info(self.hass):
            if service_info.address in known:
                continue
            if not is_dot_advertisement(service_info.name, service_info.service_uuids):
                continue
            dots[service_info.address] = f"{DEVICE_NAME} ({service_info.address})"
        return dots
