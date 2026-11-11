"""Constants for flitsmeister_dot."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "flitsmeister_dot"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_FILTER_REPLACEMENT_THRESHOLD = "filter_replacement_threshold"
DEFAULT_FILTER_REPLACEMENT_THRESHOLD = 10
