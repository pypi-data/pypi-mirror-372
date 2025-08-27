"""
Nekuda SDK - Python client for Nekuda payment processing API
"""

from .client import NekudaClient
from .exceptions import (
    NekudaError,
    NekudaApiError,
    NekudaConnectionError,
    NekudaValidationError,
    AuthenticationError,
    InvalidRequestError,
    CardNotFoundError,
    RateLimitError,
    ServerError,
)
from ._globals import get_default_client, set_default_client
from .response_models import (
    CardRevealTokenResponse,
    CardDetailsResponse,
    MandateCreateResponse,
    MandateValidationResponse,
    TransactionResponse,
    CollectCardResponse,
    RawCardDetailsResponse,
    ShortLivedTokenResponse,
    BillingDetailsResponse,
)

# Get version from package metadata (reads from pyproject.toml)
try:
    from importlib.metadata import version

    __version__ = version("nekuda")
except Exception:
    # Fallback if package not installed or in development
    __version__ = "unknown"

__all__ = [
    "NekudaClient",
    "NekudaError",
    "NekudaApiError",
    "NekudaConnectionError",
    "NekudaValidationError",
    "UserContext",
    "MandateData",
    "CardDetails",
    "AuthenticationError",
    "InvalidRequestError",
    "CardNotFoundError",
    "RateLimitError",
    "ServerError",
    "get_default_client",
    "set_default_client",
    # Response models
    "CardRevealTokenResponse",
    "CardDetailsResponse",
    "MandateCreateResponse",
    "MandateValidationResponse",
    "TransactionResponse",
    "CollectCardResponse",
    "RawCardDetailsResponse",
    "ShortLivedTokenResponse",
    "BillingDetailsResponse",
]

# Convenience re-exports for IDEs
from .user import UserContext  # noqa: E402 – re-export placed after __all__
from .models import (
    MandateData,
    CardDetails,
)
