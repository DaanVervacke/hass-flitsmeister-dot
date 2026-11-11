"""Config flow discovery shim. Hassfest requires this module at the integration root."""

from .config_flow_handler import FlitsmeisterDotConfigFlowHandler

__all__ = ["FlitsmeisterDotConfigFlowHandler"]
