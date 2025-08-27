"""Validation utilities for the Nekuda SDK."""

import json
from typing import Dict, Any, Union, Optional, TypeVar, Type
import httpx
from pydantic import BaseModel

from ..exceptions import NekudaApiError
from ..response_models import validate_and_parse_response

T = TypeVar("T", bound=BaseModel)


def validate_json_response(
    response: httpx.Response,
    expect_dict: bool = False,
    response_model: Optional[Type[BaseModel]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, Any], BaseModel]:
    """Validate and parse JSON response from the API.

    This function handles various edge cases like HTML error pages,
    invalid JSON, and ensures we get the expected response format.
    Optionally validates against a Pydantic model.

    Args:
        response: The httpx Response object
        expect_dict: If True, ensure response is a dict (wrap arrays if needed)
        response_model: Optional Pydantic model to validate response against
        context: Optional context for error handling

    Returns:
        Parsed JSON response as dict, or validated Pydantic model instance

    Raises:
        NekudaApiError: If response is not valid JSON or is an HTML error page
        NekudaValidationError: If response doesn't match the expected model
    """
    # Check for HTML error responses (common with nginx/gateway errors)
    content_type = response.headers.get("content-type", "").lower()
    if "text/html" in content_type:
        # Try to extract error message from HTML
        error_msg = "HTML error response received"
        error_code = "html_error"

        if response.status_code:
            error_msg = f"HTML error response (HTTP {response.status_code})"

        # Look for common error patterns in HTML
        text = response.text.lower()
        if "nginx" in text:
            error_msg = f"Server error (nginx): HTTP {response.status_code}"
            error_code = "nginx_error"
        elif "502 bad gateway" in text:
            error_msg = "502 Bad Gateway error from server"
            error_code = "bad_gateway"
        elif "503 service unavailable" in text:
            error_msg = "503 Service Unavailable error from server"
            error_code = "service_unavailable"
        elif "504 gateway timeout" in text:
            error_msg = "504 Gateway Timeout error from server"
            error_code = "gateway_timeout"

        raise NekudaApiError(
            message=error_msg, code=error_code, status_code=response.status_code
        )

    # Try to parse as JSON
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        # Check if it might be an HTML response even without proper content-type
        if response.text.strip().startswith("<"):
            raise NekudaApiError(
                message=f"HTML response received when JSON was expected (HTTP {response.status_code})",
                code="html_error",
                status_code=response.status_code,
            )

        raise NekudaApiError(
            message=f"Invalid JSON response: {str(e)}",
            code="invalid_json",
            status_code=response.status_code,
        )
    except Exception as e:
        raise NekudaApiError(
            message=f"Failed to parse response: {str(e)}",
            code="parse_error",
            status_code=getattr(response, "status_code", 0),
        )

    # If we expect a dict but got something else, wrap it
    if expect_dict and not isinstance(data, dict):
        data = {"data": data}

    # If a response model is provided, validate against it
    if response_model:
        return validate_and_parse_response(data, response_model, context)  # type: ignore[return-value]

    return data
