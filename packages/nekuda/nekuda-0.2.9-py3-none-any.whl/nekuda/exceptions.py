"""
Exception classes for Nekuda SDK
"""

import httpx
from typing import Dict, Any, Optional


class NekudaError(Exception):
    """Base exception for all Nekuda SDK errors"""

    pass


class NekudaApiError(NekudaError):
    """Exception raised for API errors"""

    def __init__(self, message: str, code: str, status_code: int):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(f"[{code}] {message}")


class NekudaConnectionError(NekudaError):
    """Exception raised for connection errors"""

    pass


class NekudaValidationError(NekudaError):
    """Exception raised for validation errors"""

    pass


# ----------------------------------------------------------------------
# Granular exception hierarchy ---------
# ----------------------------------------------------------------------


class AuthenticationError(NekudaApiError):
    """401 – API key missing or invalid."""


class InvalidRequestError(NekudaApiError):
    """400/404 – Invalid parameters or resource not found."""


class CardNotFoundError(InvalidRequestError):
    """404 – Card details not found for user (specific case)."""

    def __init__(
        self, message: str, code: str, status_code: int, user_id: Optional[str] = None
    ):
        self.user_id = user_id
        super().__init__(message, code, status_code)


class RateLimitError(NekudaApiError):
    """429 – Too many requests."""


class ServerError(NekudaApiError):
    """5xx – Internal error on Nekuda side."""


# ----------------------------------------------------------------------
# Error parsing utilities -----------------------------------------------
# ----------------------------------------------------------------------


def create_helpful_card_not_found_message(user_id: Optional[str] = None) -> str:
    """Create a helpful error message for card not found scenarios."""
    base_message = (
        "Card details not found. This usually means:\n"
        "1. No payment information has been collected for this user yet\n"
        "2. You're using a different user_id than was used during card collection\n"
        "3. The card data may have expired or been cleaned up\n"
    )

    if user_id:
        base_message += f"→ Ensure the user '{user_id}' has completed card collection with the same user_id"
    else:
        base_message += (
            "→ Ensure the user has completed card collection with the same user_id"
        )

    return base_message


def parse_error_response(
    response: httpx.Response, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Parse an HTTP error response and extract meaningful error information.

    Args:
        response: The HTTP response object
        context: Optional context like user_id for better error messages

    Returns:
        Dict with 'message', 'code', and 'exception_class' keys
    """
    error_message = "Unknown error"
    error_code = "unknown"
    exception_class = NekudaApiError

    try:
        error_data = response.json()

        # Handle FastAPI's standard error format
        if isinstance(error_data, dict):
            # FastAPI returns errors with 'detail' field
            if "detail" in error_data:
                detail = error_data["detail"]

                # Handle validation errors (422) which have a special structure
                if isinstance(detail, list) and response.status_code == 422:
                    # Parse validation errors
                    error_parts = []
                    for err in detail:
                        loc = " → ".join(str(x) for x in err.get("loc", []))
                        msg = err.get("msg", "validation error")
                        error_parts.append(f"{loc}: {msg}")
                    error_message = "Validation error: " + "; ".join(error_parts)
                    error_code = "validation_error"
                elif isinstance(detail, str):
                    error_message = detail

                    # Generate meaningful error codes from the message
                    detail_lower = detail.lower()
                    if (
                        "invalid private key" in detail_lower
                        or "invalid api key" in detail_lower
                    ):
                        error_code = "invalid_api_key"
                    elif (
                        "authentication" in detail_lower
                        or "unauthorized" in detail_lower
                    ):
                        error_code = "authentication_error"
                    elif "not found" in detail_lower:
                        error_code = "not_found"
                    elif "rate limit" in detail_lower:
                        error_code = "rate_limit_exceeded"
                    elif "validation" in detail_lower:
                        error_code = "validation_error"
                    elif "server error" in detail_lower:
                        error_code = "server_error"

                    # Handle specific error scenarios with helpful messages
                    if (
                        response.status_code == 404
                        and "card details not found" in detail_lower
                    ):
                        user_id = context.get("user_id") if context else None
                        error_message = create_helpful_card_not_found_message(user_id)
                        error_code = "card_not_found"
                        exception_class = CardNotFoundError

                elif isinstance(detail, dict):
                    # Sometimes detail is a nested dict from dot-service
                    error_message = str(
                        detail.get("message", detail.get("detail", str(detail)))
                    )
                else:
                    error_message = str(detail)

            # Also check for 'message' field (legacy or custom format)
            elif "message" in error_data:
                error_message = error_data["message"]
                error_code = error_data.get("code", "unknown")

            # Extract any additional context
            if "code" in error_data and error_code == "unknown":
                error_code = error_data["code"]

    except (ValueError, KeyError, TypeError):
        # If JSON parsing fails or structure is unexpected
        error_message = response.text or f"HTTP {response.status_code} Error"
        error_code = "http_error"

    # Add status code to message for better debugging (but avoid duplicates)
    if str(response.status_code) not in error_message:
        error_message = f"{error_message} (Status: {response.status_code})"

    # Determine exception class based on status code
    status = response.status_code
    if exception_class == NekudaApiError:  # Only override if not already set
        if status == 401:
            exception_class = AuthenticationError
            if error_code == "unknown":
                error_code = "authentication_failed"
        elif status == 429:
            exception_class = RateLimitError
            if error_code == "unknown":
                error_code = "rate_limit_exceeded"
        elif status >= 500:
            exception_class = ServerError
            if error_code == "unknown":
                error_code = "server_error"
        elif 400 <= status < 500:
            exception_class = InvalidRequestError
            if error_code == "unknown":
                error_code = "invalid_request"

    return {
        "message": error_message,
        "code": error_code,
        "status_code": status,
        "exception_class": exception_class,
        "context": context or {},
    }


def raise_for_error_response(
    response: httpx.Response, context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Parse an error response and raise the appropriate exception.

    Args:
        response: The HTTP response object
        context: Optional context like user_id for better error messages

    Raises:
        Appropriate NekudaError subclass
    """
    error_info = parse_error_response(response, context)

    exception_class = error_info["exception_class"]
    message = error_info["message"]
    code = error_info["code"]
    status_code = error_info["status_code"]

    # Handle special cases that need extra context
    if exception_class == CardNotFoundError:
        user_id = context.get("user_id") if context else None
        raise CardNotFoundError(message, code, status_code, user_id)
    else:
        raise exception_class(message, code, status_code)
