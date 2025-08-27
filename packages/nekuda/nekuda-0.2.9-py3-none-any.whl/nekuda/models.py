from __future__ import annotations

"""Typed request/response models used by Nekuda SDK public-API.

These dataclasses exist only to provide *developer ergonomics* – rich type
hints, IDE auto-completion and basic client-side validation.  They purposefully
avoid pulling in heavyweight runtime dependencies such as **pydantic** to keep
the SDK lightweight.
"""

import sys
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Mapping, Optional, Literal

from .exceptions import NekudaValidationError

# Python 3.10+ supports slots in dataclasses, older versions don't
_DATACLASS_KWARGS = {"slots": True} if sys.version_info >= (3, 10) else {}


@dataclass(**_DATACLASS_KWARGS)
class MandateData:
    """Schema representing a *mandate* (purchase intent) payload.

    Required fields are kept explicit while optional parameters default to
    ``None``.  Validation is executed in :py:meth:`__post_init__` and raises
    :class:`nekuda.exceptions.NekudaValidationError` when the payload is
    invalid.

    The request_id is automatically generated and cannot be overridden.
    """

    # Business & pricing information ----------------------------------
    product: Optional[str] = None
    product_description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    merchant: Optional[str] = None
    merchant_link: Optional[str] = None

    # Contextual / conversational metadata ---------------------------
    confidence_score: Optional[float] = None
    conversation_context: Optional[Mapping[str, Any]] = None
    human_messages: Optional[List[str]] = None
    additional_details: Optional[Mapping[str, Any]] = None

    # Mode specification ---------------------------------------------
    mode: Literal["live", "sandbox"] = "live"

    # Internal: unique idempotency key (automatically generated)
    request_id: str = field(
        default_factory=lambda: str(uuid.uuid4()), init=False, repr=False
    )

    # ---------------------------------------------------------------------
    # Dataclass life-cycle hooks
    # ---------------------------------------------------------------------
    def __post_init__(self) -> None:  # noqa: D401 – simple validator
        # Only perform validations on values that ARE provided.
        if self.price is not None and self.price <= 0:
            raise NekudaValidationError("'price' must be greater than 0 when provided")

        if self.confidence_score is not None and not (0 <= self.confidence_score <= 1):
            raise NekudaValidationError("'confidence_score' must be between 0 and 1")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def as_dict(self) -> Dict[str, Any]:
        """Return a JSON-serialisable dictionary representation including request_id."""

        # Include all fields, including request_id, and omit None values.
        payload = asdict(self)
        return {k: v for k, v in payload.items() if v is not None}


@dataclass(**_DATACLASS_KWARGS)
class CardDetails:
    """Represents the response from *reveal card details* endpoint."""

    card_number: str
    card_exp: str
    card_holder: str
    card_cvv: Optional[str] = None

    @classmethod
    def from_api(cls, data: Mapping[str, Any]) -> "CardDetails":
        try:
            return cls(
                card_number=str(data["card_number"]),
                card_exp=str(data["card_exp"]),
                card_holder=str(data["card_holder"]),
                card_cvv=str(data["card_cvv"]) if "card_cvv" in data else None,
            )
        except KeyError as exc:
            missing = ", ".join(exc.args)
            raise NekudaValidationError(f"Missing expected card field(s): {missing}")
