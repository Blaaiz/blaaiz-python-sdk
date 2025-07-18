"""
Currency Service
"""

from typing import Dict, Any


class CurrencyService:
    """Service for managing currencies."""

    def __init__(self, client):
        self.client = client

    def list(self) -> Dict[str, Any]:
        """
        List all currencies.

        Returns:
            API response containing list of currencies
        """
        return self.client.make_request("GET", "/api/external/currency")
