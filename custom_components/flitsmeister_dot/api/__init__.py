"""
API package for flitsmeister_dot.

Exception hierarchy:
    FlitsmeisterDotApiClientError (base)
    ├── FlitsmeisterDotApiClientCommunicationError (network/timeout)
    │   └── FlitsmeisterDotApiClientRateLimitError (429, carries retry_after)
    └── FlitsmeisterDotApiClientAuthenticationError (401/403)

The coordinator maps them onto ConfigEntryAuthFailed and UpdateFailed; nothing else
in the integration imports this package.
"""

from .client import (
    FAN_SPEEDS,
    FlitsmeisterDotApiClient,
    FlitsmeisterDotApiClientAuthenticationError,
    FlitsmeisterDotApiClientCommunicationError,
    FlitsmeisterDotApiClientError,
    FlitsmeisterDotApiClientRateLimitError,
)

__all__ = [
    "FAN_SPEEDS",
    "FlitsmeisterDotApiClient",
    "FlitsmeisterDotApiClientAuthenticationError",
    "FlitsmeisterDotApiClientCommunicationError",
    "FlitsmeisterDotApiClientError",
    "FlitsmeisterDotApiClientRateLimitError",
]
