"""Session coordinator for the Flitsmeister DOT.

The DOT sleeps while it is parked and wakes on accelerometer motion.
The coordinator connects while the DOT is visible and pushes every
decoded value to the entities. Home Assistant only reports an
advertisement when its content changes, and the DOT always sends the
same one, so a reconnect loop with a growing delay brings the session
back after a lost link or a failed attempt instead of waiting for an
advertisement that never arrives.
"""

import asyncio
from typing import TYPE_CHECKING

from bleak.backends.device import BLEDevice
from flitsmeister_dot_ble import (
    BleakTransport,
    DotAnimation,
    DotButtonEvent,
    DotError,
    DotNotReadyError,
    DotState,
    DotUpdate,
    FlitsmeisterDotClient,
    Volume,
    animations,
)

from custom_components.flitsmeister_dot.const import DOMAIN, LOGGER
from homeassistant.components.bluetooth import (
    BluetoothChange,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
    async_register_callback,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable

    from flitsmeister_dot_ble import Brightness, LedOrientation

    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry

RECONNECT_DELAYS: tuple[float, ...] = (5.0, 10.0, 30.0, 60.0)


class FlitsmeisterDotCoordinator(DataUpdateCoordinator[DotState]):
    """Keep one DOT session alive and push its values to the entities."""

    config_entry: FlitsmeisterDotConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: FlitsmeisterDotConfigEntry,
    ) -> None:
        """Set up the coordinator for one config entry."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
        )
        self.last_update_success = False
        self.client: FlitsmeisterDotClient | None = None
        self._unsub_advertisements: Callable[[], None] | None = None
        self._reconnect_task: asyncio.Task[None] | None = None
        self._stopping = False
        self._failures = 0
        self._event_seq = 0
        self._latest_event: DotButtonEvent | None = None
        self._volume: Volume | None = None

    @property
    def address(self) -> str:
        """The Bluetooth address of the DOT."""
        return self.config_entry.data[CONF_ADDRESS]

    @property
    def volume(self) -> Volume | None:
        """The volume written to the DOT on every connect."""
        return self._volume

    @property
    def latest_event(self) -> DotButtonEvent | None:
        """The most recent button event."""
        return self._latest_event

    @property
    def event_seq(self) -> int:
        """The number of button events seen so far."""
        return self._event_seq

    @callback
    def async_start(self) -> None:
        """Listen for the DOT's advertisements and connect when it is seen."""
        self._unsub_advertisements = async_register_callback(
            self.hass,
            self._async_on_advertisement,
            {"address": self.address},
            BluetoothScanningMode.ACTIVE,
        )

    async def async_stop(self) -> None:
        """Stop reconnecting and disconnect the DOT."""
        self._stopping = True
        if self._unsub_advertisements is not None:
            self._unsub_advertisements()
            self._unsub_advertisements = None
        task = self._reconnect_task
        self._reconnect_task = None
        if task is not None and not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        client = self.client
        self.client = None
        if client is not None:
            await client.disconnect()

    async def async_set_volume(self, volume: Volume) -> None:
        """Store the volume and write it to the DOT when its session is ready."""
        self._volume = volume
        client = self.client
        if client is not None and client.ready:
            await client.set_volume(volume)

    @callback
    def async_restore_volume(self, volume: Volume) -> None:
        """Adopt the volume the volume entity restored after a restart."""
        self._volume = volume

    async def async_set_brightness(self, brightness: Brightness) -> None:
        """Set the LED brightness on the DOT."""
        await self._require_ready().set_brightness(brightness)

    async def async_set_led_orientation(self, orientation: LedOrientation) -> None:
        """Set the LED ring orientation on the DOT."""
        await self._require_ready().set_led_orientation(orientation)

    async def async_play_animation(self, animation: DotAnimation) -> None:
        """Play one animation on the DOT."""
        await self._require_ready().play_animation(animation)

    @callback
    def _async_on_advertisement(
        self,
        service_info: BluetoothServiceInfoBleak,
        change: BluetoothChange,
    ) -> None:
        self._async_ensure_reconnecting()

    @callback
    def _async_ensure_reconnecting(self) -> None:
        if self._stopping or self.hass.is_stopping:
            return
        client = self.client
        if client is not None and client.connected:
            return
        task = self._reconnect_task
        if task is not None and not task.done():
            return
        self._reconnect_task = self.config_entry.async_create_background_task(
            self.hass,
            self._async_reconnect_loop(),
            f"{DOMAIN} reconnect {self.address}",
        )

    async def _async_reconnect_loop(self) -> None:
        attempt = 0
        while not self._stopping:
            device = async_ble_device_from_address(self.hass, self.address, connectable=True)
            if device is None:
                LOGGER.debug("The DOT at %s is out of reach, waiting for its next advertisement", self.address)
                return
            if await self._async_connect(device):
                return
            delay = RECONNECT_DELAYS[min(attempt, len(RECONNECT_DELAYS) - 1)]
            attempt += 1
            await asyncio.sleep(delay)

    async def _async_connect(self, device: BLEDevice) -> bool:
        client = self._build_client(device)
        try:
            await client.connect()
            if self._volume is not None:
                await client.set_volume(self._volume)
            await client.play_animation(animations.startup())
            await client.read_settings()
        except asyncio.CancelledError:
            await client.disconnect()
            raise
        except DotError as error:
            await client.disconnect()
            self._async_log_failure(error)
            return False
        if self._failures:
            LOGGER.info("Reconnected to the DOT at %s", self.address)
        self._failures = 0
        self.client = client
        self._async_update_device(client.state)
        self.async_set_updated_data(client.state)
        return True

    @callback
    def _async_log_failure(self, error: DotError) -> None:
        self._failures += 1
        cause = error.__cause__ or error
        if self._failures == 1:
            LOGGER.warning("Connecting to the DOT at %s failed, retrying: %s", self.address, cause)
            return
        LOGGER.debug("Connecting to the DOT at %s failed again: %s", self.address, cause)

    def _build_client(self, device: BLEDevice) -> FlitsmeisterDotClient:
        return FlitsmeisterDotClient(
            BleakTransport(device, ble_device_callback=lambda: self._latest_device(device)),
            update_callback=self._async_on_update,
            connection_lost_callback=self._async_on_connection_lost,
        )

    def _latest_device(self, fallback: BLEDevice) -> BLEDevice:
        return async_ble_device_from_address(self.hass, self.address, connectable=True) or fallback

    @callback
    def _async_on_update(self, update: DotUpdate) -> None:
        if update.button is not None:
            self._latest_event = update.button
            self._event_seq += 1
        elif self.last_update_success and update.state == self.data:
            return
        self.async_set_updated_data(update.state)

    @callback
    def _async_on_connection_lost(self, error: Exception) -> None:
        LOGGER.info("Lost the connection to the DOT at %s: %s", self.address, error)
        self.client = None
        self.last_update_success = False
        self.async_update_listeners()
        self._async_ensure_reconnecting()

    @callback
    def _async_update_device(self, state: DotState) -> None:
        registry = dr.async_get(self.hass)
        device = registry.async_get_device_by_identifier((DOMAIN, self.address), self.config_entry.entry_id)
        if device is None:
            return
        registry.async_update_device(
            device.id,
            manufacturer=state.manufacturer_name or device.manufacturer,
            model=state.model_number or device.model,
            sw_version=state.firmware_revision or device.sw_version,
            serial_number=state.serial_uuid or device.serial_number,
        )

    def _require_ready(self) -> FlitsmeisterDotClient:
        client = self.client
        if client is None or not client.ready:
            raise DotNotReadyError("The DOT is not connected")
        return client
