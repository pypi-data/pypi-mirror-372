"""Response models for Nekuda SDK.

These models provide type safety and validation for API responses.
Based on the API gateway models to ensure consistency.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re


# Card/Wallet Response Models
# ---------------------------


class CardRevealTokenResponse(BaseModel):
    """Response model for card reveal token request."""

    reveal_token: str = Field(
        ..., alias="token", description="One-time token for revealing card details"
    )
    expires_at: Optional[datetime] = Field(None, description="Token expiration time")

    model_config = ConfigDict(populate_by_name=True)


class CardDetailsResponse(BaseModel):
    """Response model for revealed card details."""

    card_number: str = Field(..., description="Full card number")
    card_expiry_date: str = Field(
        ..., alias="card_exp", description="Card expiry date (MM/YY)"
    )
    cardholder_name: str = Field(..., alias="card_holder", description="Name on card")
    last4_digits: Optional[str] = Field(None, description="Last 4 digits of card")
    card_cvv: Optional[str] = Field(None, description="Card CVV")

    # Additional fields that might be returned
    email: Optional[str] = Field(None, description="Email associated with the card")
    billing_address: Optional[str] = Field(None, description="Billing address")
    zip_code: Optional[str] = Field(None, description="Billing ZIP code")
    phone_number: Optional[str] = Field(None, description="Phone number")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",  # Ignore extra fields from API
    )

    @field_validator("card_expiry_date")
    @classmethod
    def validate_expiry_format(cls, v: str) -> str:
        """Validate card expiry date format."""
        if not re.match(r"^\d{2}/\d{2}$", v):
            raise ValueError("Card expiry must be in MM/YY format")
        return v

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Basic card number validation."""
        # Remove spaces and validate it's numeric
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Card number must contain only digits")
        if len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError("Card number must be between 13 and 19 digits")
        return v


# Mandate Response Models
# ----------------------


class MandateCreateResponse(BaseModel):
    """Response model for mandate creation."""

    mandate_id: int = Field(..., description="Unique identifier for the mandate")
    request_id: str = Field(..., description="Request ID for tracking")
    customer_id: str = Field(..., description="Customer identifier")
    created_at: datetime = Field(..., description="Mandate creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(populate_by_name=True)


class MandateValidationResponse(BaseModel):
    """Response model for mandate validation."""

    mandate_id: str = Field(..., description="The ID of the validated mandate")
    is_valid: bool = Field(..., description="Whether the mandate is valid")
    reason: Optional[str] = Field(None, description="Validation failure reason")
    status_code_hint: Optional[int] = Field(None, description="HTTP status code hint")

    model_config = ConfigDict(populate_by_name=True)


# Transaction Response Models
# --------------------------


class TransactionResponse(BaseModel):
    """Response model for transaction operations."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    status: Optional[str] = Field(None, description="Transaction status")
    message: Optional[str] = Field(None, description="Status message")

    model_config = ConfigDict(populate_by_name=True)


# Collection Response Models
# -------------------------


class CollectCardResponse(BaseModel):
    """Response model for card collection."""

    status: str = Field(..., description="Collection status")
    message: str = Field(..., description="Status message")
    request_id: str = Field(..., description="Request tracking ID")
    id: str = Field(..., description="Saved card identifier")

    model_config = ConfigDict(populate_by_name=True)


# Generic Response Wrapper
# -----------------------


class ApiResponse(BaseModel):
    """Generic API response wrapper for consistent error handling."""

    success: bool = Field(True, description="Whether the request succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details if failed")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

    model_config = ConfigDict(populate_by_name=True)


# Enhanced API Response Models
# ----------------------------


class RawCardDetailsResponse(BaseModel):
    """Response model for RAW card details - CONTAINS SENSITIVE DATA!

    WARNING: This model contains full card numbers and should only be used
    in highly secure, tokenized contexts (e.g., reveal token flows).
    Use CardDetailsResponse for regular API responses.

    Enhanced version for reveal endpoint that explicitly includes card_number.
    """

    # Sensitive card data
    card_number: str = Field(..., description="Card number")
    card_exp: str = Field(..., description="Card expiry date")
    card_holder: str = Field(..., description="Card holder name")
    card_cvv: Optional[str] = Field(
        None, description="Card CVV (sensitive - input only)"
    )

    # Contact and billing information (required)
    email: str = Field(..., description="Cardholder email")
    phone_number: str = Field(..., description="Cardholder phone number")
    billing_address: str = Field(..., description="Billing address line")
    zip_code: str = Field(..., description="Billing address ZIP code")

    # Optional location fields
    city: Optional[str] = Field(None, description="Billing city")
    state: Optional[str] = Field(None, description="Billing state")

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    @field_validator("card_exp")
    @classmethod
    def validate_expiry_format(cls, v: str) -> str:
        """Validate card expiry date format."""
        if not re.match(r"^\d{2}/\d{2}$", v):
            raise ValueError("Card expiry must be in MM/YY format")
        return v

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        """Basic card number validation."""
        # Remove spaces and validate it's numeric
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Card number must contain only digits")
        if len(cleaned) < 13 or len(cleaned) > 19:
            raise ValueError("Card number must be between 13 and 19 digits")
        return v


class ShortLivedTokenResponse(BaseModel):
    """Response model for card reveal token request.

    Updated response format that uses 'token' field instead of 'reveal_token'.
    """

    token: str = Field(..., description="Short-lived token for revealing card details")
    expires_at: datetime = Field(..., description="Token expiration time")

    model_config = ConfigDict(populate_by_name=True)


class BillingDetailsResponse(BaseModel):
    """Response model for billing/shipping details (no sensitive card data).

    This model contains only non-sensitive information needed for billing,
    shipping, and contact purposes, excluding all payment card details.
    """

    # User identification
    user_id: str = Field(..., description="User identifier")

    # Contact information
    card_holder: str = Field(..., description="User/cardholder name")
    phone_number: str = Field(..., description="Contact phone number")

    # Billing/shipping address
    billing_address: str = Field(..., description="Full street address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/province")
    zip_code: str = Field(..., description="ZIP/postal code")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "user_id": "user_12345",
                "card_holder": "John Doe",
                "phone_number": "+12125551234",
                "billing_address": "123 Main Street, Apt 4B",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
            }
        },
    )


# Response Validation Utilities
# ----------------------------


def validate_and_parse_response(
    response_data: Dict[str, Any],
    response_model: type[BaseModel],
    context: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    """Validate response data against a Pydantic model.

    Args:
        response_data: Raw response dictionary from API
        response_model: Pydantic model class to validate against
        context: Optional context for error messages

    Returns:
        Validated model instance

    Raises:
        NekudaValidationError: If validation fails
    """
    from .exceptions import NekudaValidationError

    try:
        return response_model.model_validate(response_data)
    except ValueError as e:
        # Extract validation errors
        error_details = []
        if hasattr(e, "errors"):
            for error in e.errors():
                field = " -> ".join(str(x) for x in error.get("loc", []))
                msg = error.get("msg", "validation error")
                error_details.append(f"{field}: {msg}")

        error_message = f"Response validation failed for {response_model.__name__}: "
        if error_details:
            error_message += "; ".join(error_details)
        else:
            error_message += str(e)

        # Add context if provided
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            error_message += f" (Context: {context_str})"

        raise NekudaValidationError(error_message)
