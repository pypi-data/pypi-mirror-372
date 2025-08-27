from __future__ import annotations

"""User context helper that automatically injects the *user_id* into every
Nekuda SDK call.  Returned by :py:meth:`nekuda.NekudaClient.user`.
"""

from typing import Any, Dict, Optional, Union

from .client import NekudaClient
from .models import CardDetails, MandateData
from .response_models import (
    CardRevealTokenResponse,
    CardDetailsResponse,
    MandateCreateResponse,
    ShortLivedTokenResponse,
    RawCardDetailsResponse,
    BillingDetailsResponse,
)

__all__ = ["UserContext"]


class UserContext:  # noqa: D101 – docstring below
    """A thin immutable wrapper around :class:`~nekuda.NekudaClient` that
    pins a specific ``user_id``.  This aids readability & reduces repetitive
    parameter passing, especially when an application iterates over many users
    concurrently.

    Instances are *cheap* to create – they only hold two references (client &
    the user_id string) and delegate all network I/O to the shared
    :class:`~nekuda.NekudaClient`.
    """

    __slots__ = ("_client", "user_id")

    def __init__(self, client: NekudaClient, user_id: str) -> None:  # noqa: D401
        if user_id is None:
            raise TypeError("user_id cannot be None")
        if not user_id:
            raise ValueError("user_id cannot be empty")
        self._client = client
        self.user_id = user_id

    # ------------------------------------------------------------------
    # High-level workflows
    # ------------------------------------------------------------------
    def create_mandate(self, mandate: MandateData) -> MandateCreateResponse:
        """Create a mandate for this user.

        Parameters
        ----------
        mandate:
            The :class:`~nekuda.models.MandateData` describing the purchase
            intent. The request_id is automatically generated.

        Returns
        -------
        MandateCreateResponse:
            The created mandate details
        """
        return self._client.create_mandate(
            user_id=self.user_id,
            mandate_data=mandate,
        )

    # Delegated helpers --------------------------------------------------
    def request_card_reveal_token(
        self, mandate_id: Union[str, int]
    ) -> ShortLivedTokenResponse:
        """Request a card reveal token for this user.

        Parameters
        ----------
        mandate_id:
            The mandate ID to use for the reveal

        Returns
        -------
        ShortLivedTokenResponse:
            The reveal token and expiration time
        """
        return self._client.request_card_reveal_token(
            user_id=self.user_id,
            mandate_id=str(mandate_id),
        )

    def reveal_card_details(self, reveal_token: str) -> RawCardDetailsResponse:
        """Reveal card details using a token.

        Parameters
        ----------
        reveal_token:
            The one-time token obtained from request_card_reveal_token

        Returns
        -------
        CardDetailsResponse:
            The revealed card details
        """
        return self._client.reveal_card_details(
            user_id=self.user_id,
            reveal_token=reveal_token,
        )

    def get_billing_details(self) -> BillingDetailsResponse:
        """Get billing details for this user without sensitive card data.

        The customer_id is automatically derived from the API key context.

        Returns
        -------
        BillingDetailsResponse:
            Billing address and contact information
        """
        return self._client.get_billing_details(user_id=self.user_id)

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # noqa: D401 – simple repr
        return f"<UserContext user_id='{self.user_id}'>"
