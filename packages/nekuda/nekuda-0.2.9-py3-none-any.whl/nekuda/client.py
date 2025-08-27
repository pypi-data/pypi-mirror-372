"""
Main client for Nekuda SDK
"""

import httpx
from typing import Dict, Optional, Any, Union, TypeVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserContext
import time
import os
import logging

from .exceptions import NekudaConnectionError
from .utils.http import normalize_url
from .utils.validation import validate_json_response
from .models import MandateData
from .response_models import (
    MandateCreateResponse,
    ShortLivedTokenResponse,
    RawCardDetailsResponse,
    BillingDetailsResponse,
)

# Set up logger for the SDK
logger = logging.getLogger("nekuda")

T = TypeVar("T")


class NekudaClient:
    """Client for Nekuda SDK to interact with payment API"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.nekuda.ai",
        timeout: int = 30,
        *,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        """
        Initialize the Nekuda SDK client

        Args:
            api_key: Customer's API key
            base_url: Base URL for the Nekuda API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for HTTP requests
            backoff_factor: Factor to increase wait time between retries
        """
        # Import version here to avoid circular imports
        try:
            from . import __version__

            self.version = __version__
        except ImportError:
            self.version = "unknown"

        self.api_key = api_key
        # Normalize the base URL on initialization
        self.base_url = normalize_url(base_url)
        self.timeout = timeout

        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # Lazily initialised persistent HTTP client (to enable pickling / forking)
        self._session: Optional[httpx.Client] = None

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T]:
        """
        Make an HTTP request to the API gateway

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            params: Query parameters
            extra_headers: Optional dictionary of extra headers to include
            context: Optional context for error handling (e.g., user_id)
            response_model: Optional Pydantic model for response validation

        Returns:
            API response as dictionary or validated model instance
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Base headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"nekuda-sdk-python/{self.version}",
        }
        if extra_headers:
            headers.update(extra_headers)

        # Log the request details (hide sensitive data)
        logger.debug(f"Making {method} request to {url}")
        if data:
            # Log payload but mask sensitive fields
            safe_data = {
                k: "***" if k in ["card_number", "card_cvv", "api_key"] else v
                for k, v in data.items()
            }
            logger.debug(f"Request payload: {safe_data}")
        logger.debug(
            f"Request headers: {dict((k, '***' if 'key' in k.lower() or 'auth' in k.lower() else v) for k, v in headers.items())}"
        )

        # Ensure we have a persistent session
        if self._session is None:
            self._session = httpx.Client(timeout=self.timeout)

        # Retry loop ----------------------------------------------------
        attempt = 0
        while True:
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers,
                )

                logger.debug(f"Response status: {response.status_code}")

                response.raise_for_status()

                # Use our new validation function with optional model
                response_data = validate_json_response(  # type: ignore[misc,arg-type]
                    response,
                    expect_dict=True,
                    response_model=response_model,  # type: ignore[arg-type]
                    context=context,
                )

                # Log successful response (mask sensitive data)
                if logger.isEnabledFor(logging.DEBUG) and isinstance(
                    response_data, dict
                ):
                    safe_response = {
                        k: (
                            "***"
                            if k in ["card_number", "card_cvv", "reveal_token", "token"]
                            else v
                        )
                        for k, v in response_data.items()
                    }
                    logger.debug(f"Response data: {safe_response}")

                return response_data  # type: ignore[return-value]
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                logger.warning(
                    f"HTTP error {status} on attempt {attempt + 1}/{self.max_retries + 1}"
                )

                should_retry = status == 429 or status >= 500
                if should_retry and attempt < self.max_retries:
                    sleep_for = self.backoff_factor * 2**attempt
                    logger.debug(f"Retrying after {sleep_for}s...")
                    time.sleep(sleep_for)
                    attempt += 1
                    continue

                # Log the error response
                try:
                    error_body = exc.response.json()
                    logger.error(f"Error response: {error_body}")
                except (ValueError, TypeError, AttributeError):
                    logger.error(f"Error response (raw): {exc.response.text}")

                self._handle_error_response(exc.response, context)
            except httpx.RequestError as exc:
                logger.warning(
                    f"Request error on attempt {attempt + 1}/{self.max_retries + 1}: {str(exc)}"
                )

                if attempt < self.max_retries:
                    sleep_for = self.backoff_factor * 2**attempt
                    logger.debug(f"Retrying after {sleep_for}s...")
                    time.sleep(sleep_for)
                    attempt += 1
                    continue

                # Provide more helpful error messages for common connection issues
                error_msg = str(exc)
                if (
                    "nodename nor servname provided" in error_msg
                    or "Name or service not known" in error_msg
                ):
                    raise NekudaConnectionError(
                        f"Failed to resolve hostname: {url}\n"
                        f"Please check:\n"
                        f"1. The NEKUDA_BASE_URL environment variable is set correctly\n"
                        f"2. You have a working internet connection\n"
                        f"3. The API hostname is valid (current: {self.base_url})"
                    )
                elif "Connection refused" in error_msg:
                    raise NekudaConnectionError(
                        f"Connection refused to {url}\n"
                        f"The server may be down or not accepting connections on this port."
                    )
                elif "timeout" in error_msg.lower():
                    raise NekudaConnectionError(
                        f"Request timed out after {self.timeout} seconds.\n"
                        f"Try increasing the timeout or check your network connection."
                    )
                else:
                    raise NekudaConnectionError(f"Connection error: {error_msg}")

    def request_card_reveal_token(
        self, user_id: str, mandate_id: Union[str, int]
    ) -> ShortLivedTokenResponse:
        """
        Request a one-time token to reveal card details for a user.

        Args:
            user_id: The identifier for the user.
            mandate_id: The identifier for the mandate to be used.

        Returns:
            ShortLivedTokenResponse containing the reveal token and expiration
        """
        endpoint = "/api/v2/wallet/request_card_reveal_token"
        headers = {
            "x-api-key": self.api_key,
            "x-user-id": user_id,
        }
        payload = {
            "mandate_id": str(mandate_id)  # Ensure mandate_id is always a string
        }
        # Pass user_id in context for better error messages
        context = {"user_id": user_id, "mandate_id": mandate_id}

        # Request with typed response
        response = self._request(
            method="POST",
            endpoint=endpoint,
            data=payload,
            extra_headers=headers,
            context=context,
            response_model=ShortLivedTokenResponse,
        )

        # Type assertion since we know we're getting a model when response_model is provided
        assert isinstance(response, ShortLivedTokenResponse)

        return response

    def reveal_card_details(
        self, user_id: str, reveal_token: str
    ) -> RawCardDetailsResponse:
        """
        Reveal card details using a previously obtained reveal token.

        Args:
            user_id: The identifier for the user.
            reveal_token: The one-time token obtained from request_card_reveal_token.

        Returns:
            RawCardDetailsResponse containing full card details including card number
        """
        endpoint = "/api/v2/wallet/reveal_card_details"
        headers = {
            "Authorization": f"Bearer {reveal_token}",  # Add Bearer prefix
            "x-user-id": user_id,
        }
        # Card reveal uses GET method and headers for auth
        # Pass user_id in context for better error messages
        context = {"user_id": user_id}
        response = self._request(
            method="GET",
            endpoint=endpoint,
            extra_headers=headers,
            context=context,
            response_model=RawCardDetailsResponse,
        )

        # Type assertion since we know we're getting a model when response_model is provided
        assert isinstance(response, RawCardDetailsResponse)
        return response

    def create_mandate(
        self, user_id: str, mandate_data: MandateData
    ) -> MandateCreateResponse:
        """
        Send mandate information to the backend before a purchase flow.

        Args:
            user_id: The identifier for the user associated with the mandate.
            mandate_data: A MandateData model containing the details of the mandate.

        Returns:
            MandateCreateResponse representing the created mandate details
        """
        # Assume a standard endpoint for mandate creation
        endpoint = "/api/v2/mandate/create"
        headers = {
            "x-api-key": self.api_key,
            "x-user-id": user_id,
        }
        # Mandate data is sent as the JSON payload using the model's as_dict method
        payload = mandate_data.as_dict()

        # Pass user_id in context for better error messages
        context = {"user_id": user_id}

        # Send the POST request
        response = self._request(
            method="POST",
            endpoint=endpoint,
            data=payload,
            extra_headers=headers,
            context=context,
            response_model=MandateCreateResponse,
        )

        # Type assertion since we know we're getting a model when response_model is provided
        assert isinstance(response, MandateCreateResponse)
        return response

    def get_billing_details(self, user_id: str) -> BillingDetailsResponse:
        """
        Get billing details for a user without sensitive card data.

        The customer_id is automatically derived from the API key context.

        Args:
            user_id: The identifier for the user

        Returns:
            BillingDetailsResponse containing billing address and contact info
        """
        endpoint = "/api/v2/wallet/get_billing_details"
        headers = {
            "x-api-key": self.api_key,
            "x-user-id": user_id,
        }

        # Pass context for better error messages
        context = {"user_id": user_id}

        # Request with typed response
        response = self._request(
            method="GET",
            endpoint=endpoint,
            extra_headers=headers,
            context=context,
            response_model=BillingDetailsResponse,
        )

        # Type assertion since we know we're getting a model when response_model is provided
        assert isinstance(response, BillingDetailsResponse)
        return response

    def _handle_error_response(
        self, response: httpx.Response, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Extract error details from response and raise appropriate exception"""
        from .exceptions import raise_for_error_response

        # Use the modular error handling utility
        raise_for_error_response(response, context)

    def user(self, user_id: str) -> "UserContext":
        """Return a :class:`~nekuda.user.UserContext` bound to *user_id*.

        This is purely a convenience wrapper so callers do not need to repeat
        the ``user_id`` argument on every invocation.
        """
        # Local import to avoid circular dependency at import time.
        from .user import UserContext  # noqa: E402

        return UserContext(client=self, user_id=user_id)

    # ------------------------------------------------------------------
    # Lifecycle management ---------------------------------------------
    # ------------------------------------------------------------------
    def close(self) -> None:  # noqa: D401 – explicit close method
        if self._session is not None:
            self._session.close()

    def __del__(self) -> None:  # noqa: D401 – ensure resources freed
        try:
            self.close()
        except Exception:  # pragma: no cover – guard against destructor errors
            pass

    # ------------------------------------------------------------------
    # Convenience constructors -----------------------------------------
    # ------------------------------------------------------------------
    @classmethod
    def from_env(
        cls,
        *,
        api_key_var: str = "NEKUDA_API_KEY",
        base_url_var: str = "NEKUDA_BASE_URL",
        **kwargs: Any,
    ) -> "NekudaClient":
        """Instantiate a client using environment variables.

        Parameters
        ----------
        api_key_var:
            Name of the environment variable holding the API key.
        base_url_var:
            Name of the environment variable holding the base URL (optional).
        **kwargs:
            Forwarded to :class:`~nekuda.client.NekudaClient` constructor
            (e.g. ``timeout``, ``max_retries``).
        """
        api_key = os.getenv(api_key_var)
        if not api_key:
            raise ValueError(
                f"Environment variable '{api_key_var}' is not set or empty"
            )

        base_url = os.getenv(base_url_var, "https://api.nekuda.ai")

        return cls(api_key=api_key, base_url=base_url, **kwargs)
