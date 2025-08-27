"""
Payment-related functionality for the Nekuda SDK
"""

from typing import Dict, Optional


class PaymentMethods:
    """
    Utility class for working with payment-related endpoints

    Note: This is a helper class that could be expanded in the future
    if additional payment-related functionality is needed.
    """

    @staticmethod
    def format_token_response(response: Dict) -> Dict[str, str]:
        """
        Format the token response for easier use

        Args:
            response: Raw API response

        Returns:
            Formatted response with token and URL
        """
        return {
            "token": response.get("token", ""),
            "url": response.get("url", ""),
            "expires_at": response.get("expires_at", ""),
        }
