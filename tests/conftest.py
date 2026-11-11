"""Shared fixtures for the Flitsmeister DOT tests."""

import asyncio
from collections.abc import Callable, Generator
from dataclasses import replace
import logging
from typing import Any
from unittest.mock import MagicMock, patch

from bleak.backends.device import BLEDevice
from flitsmeister_dot_ble import (
    Brightness,
    ButtonAction,
    ChargingState,
    ConnectionStatus,
    DotAnimation,
    DotButton,
    DotButtonEvent,
    DotConnectionError,
    DotNotReadyError,
    DotRejectedError,
    DotState,
    DotUpdate,
    LedOrientation,
    MotionStatus,
    SpeechLanguage,
    Volume,
)
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.components.bluetooth import BluetoothChange
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant

DOT_ADDRESS = "AA:BB:CC:DD:EE:FF"

CONNECTED_STATE = DotState(
    battery_level=80,
    charging_state=ChargingState.CONSUMING,
    motion_status=MotionStatus.PARKED,
    manufacturer_name="Flitsmeister",
    model_number="DOT",
    serial_raw="0011223344556677",
    serial_uuid="AABBCCDD-1122-3344-5566-77889900AABB",
    firmware_revision="2.9.0",
    software_revision="2.9.0",
    speech_language=SpeechLanguage.DUTCH,
)


class FakeDotClient:
    """In-memory DOT that mirrors the wire behaviour the coordinator relies on."""

    def __init__(
        self,
        transport: Any,
        *,
        update_callback: Any = None,
        connection_lost_callback: Any = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the fake with an empty state."""
        self.state = DotState()
        self.update_callback = update_callback
        self.connection_lost_callback = connection_lost_callback
        self.connected = False
        self.played_animations: list[DotAnimation] = []
        self.written_volumes: list[Volume] = []
        self.reject_writes = False
        self.fail_connect = False
        self.connect_gate: asyncio.Event | None = None

    @property
    def ready(self) -> bool:
        """Return whether the session is ready."""
        return self.connected

    async def connect(self) -> None:
        """Simulate the connect reads, or a DOT that does not answer."""
        if self.connect_gate is not None:
            await self.connect_gate.wait()
        if self.fail_connect:
            raise DotConnectionError("The DOT did not answer")
        self.connected = True
        self.state = CONNECTED_STATE
        self.emit_state()

    async def disconnect(self) -> None:
        """Simulate a clean disconnect."""
        self.connected = False

    async def play_animation(self, animation: DotAnimation) -> None:
        """Record one played animation."""
        self._require_ready()
        self.played_animations.append(animation)

    async def set_volume(self, volume: Volume) -> None:
        """Simulate the volume write."""
        self._require_ready()
        self.written_volumes.append(volume)
        self.state = replace(self.state, volume=volume)
        self.emit_state()

    async def set_brightness(self, brightness: Brightness) -> None:
        """Simulate the brightness write and its read back."""
        self._require_ready()
        self.state = replace(self.state, brightness=brightness)
        self.emit_state()

    async def set_led_orientation(self, orientation: LedOrientation) -> None:
        """Simulate the orientation write and its read back."""
        self._require_ready()
        self.state = replace(self.state, led_orientation=orientation)
        self.emit_state()

    async def read_settings(self) -> None:
        """Simulate the settings read."""
        self.state = replace(
            self.state,
            brightness=Brightness.BRIGHTNESS_50,
            led_orientation=LedOrientation.NORMAL,
        )
        self.emit_state()

    def press(self, button: DotButton, action: ButtonAction) -> None:
        """Simulate one button event from the device."""
        self._emit_button(DotButtonEvent(button, action))

    def drop_connection(self, error: Exception | None = None) -> None:
        """Simulate the DOT going back to sleep."""
        self.connected = False
        callback = self.connection_lost_callback
        if callback is not None:
            callback(error or DotConnectionError("The DOT disconnected"))

    def emit_state(self) -> None:
        """Notify the coordinator of the current state, changed or not."""
        self._emit_button(None)

    def _emit_button(self, button: DotButtonEvent | None) -> None:
        callback = self.update_callback
        if callback is None:
            return
        callback(
            DotUpdate(
                self.state,
                ConnectionStatus.READY if self.connected else ConnectionStatus.DISCONNECTED,
                "fake",
                b"",
                button,
            )
        )

    def _require_ready(self) -> None:
        if not self.ready:
            raise DotNotReadyError("The DOT is not connected")
        if self.reject_writes:
            raise DotRejectedError("The DOT refused the write")


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load custom integrations in every test."""


@pytest.fixture(autouse=True)
def fail_on_deprecation_report(caplog: pytest.LogCaptureFixture) -> Generator[None]:
    """Fail a test when Home Assistant logs a deprecation this integration caused."""
    yield
    reports = [
        message
        for record in [*caplog.get_records("setup"), *caplog.get_records("call")]
        if record.levelno >= logging.WARNING
        and DOMAIN in (message := record.getMessage())
        and message.startswith(("Detected that custom integration", "The deprecated"))
    ]
    assert not reports, "\n".join(reports)


class FakeDots(list[FakeDotClient]):
    """Every fake session the coordinator built, plus how many connects to fail."""

    failures_to_inject = 0
    connect_gate: asyncio.Event | None = None


class FakeBluetooth:
    """The advertisement callbacks and whether Home Assistant still sees the DOT."""

    def __init__(self) -> None:
        """Start with the DOT in reach."""
        self.callbacks: list[Callable[..., None]] = []
        self.present = True

    def advertise(self) -> None:
        """Deliver one advertisement to every registered callback."""
        for callback in self.callbacks:
            callback(MagicMock(), BluetoothChange.ADVERTISEMENT)


@pytest.fixture(autouse=True)
def instant_reconnect() -> Generator[None]:
    """Run the reconnect loop without real delays."""
    with patch(
        "custom_components.flitsmeister_dot.coordinator.base.RECONNECT_DELAYS",
        (0.0,),
    ):
        yield


@pytest.fixture
def mock_dot() -> Generator[FakeDots]:
    """Replace the DOT client class with the fake and collect every session."""
    clients = FakeDots()

    def make_client(transport: Any, **kwargs: Any) -> FakeDotClient:
        client = FakeDotClient(transport, **kwargs)
        if clients.failures_to_inject > 0:
            clients.failures_to_inject -= 1
            client.fail_connect = True
        client.connect_gate = clients.connect_gate
        clients.append(client)
        return client

    with patch(
        "custom_components.flitsmeister_dot.coordinator.base.FlitsmeisterDotClient",
        side_effect=make_client,
    ):
        yield clients


@pytest.fixture
def mock_bluetooth() -> Generator[FakeBluetooth]:
    """Let tests fire the DOT's advertisements and take it out of reach."""
    fake = FakeBluetooth()

    def register_callback(
        hass: HomeAssistant,
        callback: Callable[..., None],
        match_dict: Any,
        mode: Any,
    ) -> Callable[[], None]:
        fake.callbacks.append(callback)
        return lambda: fake.callbacks.remove(callback)

    def device_from_address(*args: Any, **kwargs: Any) -> BLEDevice | None:
        return MagicMock(spec=BLEDevice) if fake.present else None

    with (
        patch(
            "custom_components.flitsmeister_dot.coordinator.base.async_register_callback",
            side_effect=register_callback,
        ),
        patch(
            "custom_components.flitsmeister_dot.coordinator.base.async_ble_device_from_address",
            side_effect=device_from_address,
        ),
    ):
        yield fake


@pytest.fixture
def bluetooth(enable_bluetooth: None) -> None:
    """Enable the bluetooth integration with mocked adapters."""


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Return a config entry for one DOT."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Flitsmeister DOT",
        unique_id=DOT_ADDRESS,
        data={CONF_ADDRESS: DOT_ADDRESS},
    )


@pytest.fixture
async def init_integration(
    hass: HomeAssistant,
    bluetooth: None,
    mock_dot: FakeDots,
    mock_bluetooth: FakeBluetooth,
    config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up the integration before the DOT has advertised."""
    config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


@pytest.fixture
async def wake_dot(
    hass: HomeAssistant,
    mock_dot: FakeDots,
    mock_bluetooth: FakeBluetooth,
) -> Callable[[], FakeDotClient]:
    """Return a helper that fires one advertisement and returns the session."""

    async def wake() -> FakeDotClient:
        mock_bluetooth.present = True
        mock_bluetooth.advertise()
        await hass.async_block_till_done(wait_background_tasks=True)
        return mock_dot[-1]

    return wake
