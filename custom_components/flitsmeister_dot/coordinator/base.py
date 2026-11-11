"""Data update coordinator for flitsmeister_dot."""

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from custom_components.flitsmeister_dot.api import (
    FlitsmeisterDotApiClientAuthenticationError,
    FlitsmeisterDotApiClientError,
    FlitsmeisterDotApiClientRateLimitError,
)
from custom_components.flitsmeister_dot.const import (
    CONF_FILTER_REPLACEMENT_THRESHOLD,
    DEFAULT_FILTER_REPLACEMENT_THRESHOLD,
    DOMAIN,
    LOGGER,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from custom_components.flitsmeister_dot.data import FlitsmeisterDotConfigEntry
    from homeassistant.core import HomeAssistant

MIN_RETRY_AFTER = 10.0
UPDATE_INTERVAL = timedelta(hours=1)


class FlitsmeisterDotDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the device state once per interval and hand it to every entity."""

    config_entry: FlitsmeisterDotConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: FlitsmeisterDotConfigEntry) -> None:
        """Set up the coordinator for one config entry."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch the current device state and add the values derived from the entry's options.

        Returns:
            The payload entities read by key.

        Raises:
            ConfigEntryAuthFailed: If the credentials were rejected; triggers reauth.
            UpdateFailed: If the fetch failed for any other reason; after a rate limit, it carries the wait the API
                asked for.

        """
        try:
            data = await self.config_entry.runtime_data.client.async_get_data()
        except FlitsmeisterDotApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="authentication_failed",
            ) from exception
        except FlitsmeisterDotApiClientRateLimitError as exception:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                retry_after=self._bounded_retry_after(exception.retry_after),
            ) from exception
        except FlitsmeisterDotApiClientError as exception:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
            ) from exception
        else:
            threshold = self.config_entry.options.get(
                CONF_FILTER_REPLACEMENT_THRESHOLD, DEFAULT_FILTER_REPLACEMENT_THRESHOLD
            )
            return {**data, "filter_replacement": data["filter_life"] < threshold}

    def _bounded_retry_after(self, seconds: float) -> float:
        """
        Keep the wait a rate limit asks for between MIN_RETRY_AFTER and the regular update interval.

        Returns:
            The seconds until the next poll.

        """
        if self.update_interval:
            seconds = min(seconds, self.update_interval.total_seconds())
        return max(seconds, MIN_RETRY_AFTER)
