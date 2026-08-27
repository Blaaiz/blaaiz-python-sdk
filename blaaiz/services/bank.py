"""
Bank Service
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


class BankService:
    """Service for managing banks."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List all banks.

        Args:
            filters: Optional query parameters. Supported keys include
                ``currency``, ``country`` and ``country_id``.

        Returns:
            API response containing list of banks
        """
        endpoint = "/api/external/bank"
        if filters:
            params = {}
            for key, value in filters.items():
                if value is None:
                    continue
                if isinstance(value, bool):
                    params[key] = "true" if value else "false"
                else:
                    params[key] = value
            if params:
                endpoint = f"{endpoint}?{urlencode(params)}"
        return self.client.make_request("GET", endpoint)

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

    def verify_payee(self, payee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a GBP payee (confirmation of payee).

        Args:
            payee_data: Requires ``sort_code``, ``account_number`` and
                ``account_name``.

        Returns:
            API response containing the match result
        """
        required_fields = ["sort_code", "account_number", "account_name"]

        for field in required_fields:
            if not payee_data or field not in payee_data or not payee_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/bank/payee-verification", payee_data)

    def verify_iban(self, iban_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify an IBAN and its SEPA reachability.

        Args:
            iban_data: Requires ``iban``.

        Returns:
            API response containing SEPA reachability
        """
        if not iban_data or not iban_data.get("iban"):
            raise ValueError("iban is required")

        return self.client.make_request("POST", "/api/external/bank/iban-verification", iban_data)
