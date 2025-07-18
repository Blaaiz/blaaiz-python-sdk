"""
Bank Service
"""

from typing import Dict, Any


class BankService:
    """Service for managing banks."""

    def __init__(self, client):
        self.client = client

    def list(self) -> Dict[str, Any]:
        """
        List all banks.

        Returns:
            API response containing list of banks
        """
        return self.client.make_request("GET", "/api/external/bank")

    def lookup_account(self, lookup_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lookup bank account information.

        Args:
            lookup_data: Account lookup information

        Returns:
            API response containing account information
        """
        required_fields = ["account_number", "bank_id"]

        for field in required_fields:
            if field not in lookup_data or not lookup_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/bank/account-lookup", lookup_data)
