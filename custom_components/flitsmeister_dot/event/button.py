"""Button event entities for the Flitsmeister DOT integration."""

from typing import TYPE_CHECKING

from flitsmeister_dot_ble import ButtonAction, DotButton

from custom_components.flitsmeister_dot.entity import FlitsmeisterDotEntity
from homeassistant.components.event import EventEntity, EventEntityDescription
from homeassistant.core import callback

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.coordinator import FlitsmeisterDotCoordinator

BUTTON_EVENT_TYPES = [
    ButtonAction.SHORT_PRESS.name.lower(),
    ButtonAction.LONG_PRESS.name.lower(),
]

ENTITY_DESCRIPTIONS = (
    EventEntityDescription(key="red_button", translation_key="red_button"),
    EventEntityDescription(key="blue_button", translation_key="blue_button"),
)

BUTTON_BY_KEY = {
    "red_button": DotButton.RED,
    "blue_button": DotButton.BLUE,
}


class FlitsmeisterDotButtonEvent(EventEntity, FlitsmeisterDotEntity):
    """Event entity for one DOT button."""

    _attr_event_types = BUTTON_EVENT_TYPES

    def __init__(
        self,
        coordinator: FlitsmeisterDotCoordinator,
        entity_description: EventEntityDescription,
        button: DotButton,
    ) -> None:
        """Initialize the event entity."""
        super().__init__(coordinator, entity_description)
        self.button = button
        self._seen_seq = 0

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fire the resolved press events for this button."""
        event = self.coordinator.latest_event
        if (
            event is not None
            and event.button is self.button
            and event.action in (ButtonAction.SHORT_PRESS, ButtonAction.LONG_PRESS)
            and self.coordinator.event_seq != self._seen_seq
        ):
            self._seen_seq = self.coordinator.event_seq
            self._trigger_event(event.action.name.lower())
        super()._handle_coordinator_update()
