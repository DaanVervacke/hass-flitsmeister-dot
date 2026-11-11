"""Service action registration for the Flitsmeister DOT integration."""

from custom_components.flitsmeister_dot.const import DOMAIN
from homeassistant.core import HomeAssistant, ServiceCall, callback

from .play_animation import PLAY_ANIMATION_SCHEMA, async_handle_play_animation
from .play_progress import PLAY_PROGRESS_SCHEMA, async_handle_play_progress

SERVICE_PLAY_ANIMATION = "play_animation"
SERVICE_PLAY_PROGRESS = "play_progress"


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the integration's actions once, at component level."""

    async def handle_play_animation(call: ServiceCall) -> None:
        """Play one preset animation on the targeted DOT."""
        await async_handle_play_animation(hass, call)

    async def handle_play_progress(call: ServiceCall) -> None:
        """Play the approach progress animation on the targeted DOT."""
        await async_handle_play_progress(hass, call)

    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_ANIMATION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_ANIMATION,
            handle_play_animation,
            schema=PLAY_ANIMATION_SCHEMA,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_PROGRESS):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_PROGRESS,
            handle_play_progress,
            schema=PLAY_PROGRESS_SCHEMA,
        )
