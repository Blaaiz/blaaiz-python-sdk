"""
Virtual Bank Account Service
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


class VirtualBankAccountService:
    """Service for managing virtual bank accounts."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def create(self, vba_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a virtual bank account.

        Args:
            vba_data: Virtual bank account information

        Returns:
            API response containing virtual bank account data
        """
        required_fields = ["wallet_id"]

        for field in required_fields:
            if field not in vba_data or not vba_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/virtual-bank-account", vba_data)

    def list(
        self, wallet_id: Optional[str] = None, customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List virtual bank accounts.

        Args:
            wallet_id: Optional wallet ID to filter by
            customer_id: Optional customer ID to filter by

        Returns:
            API response containing list of virtual bank accounts
        """
        endpoint = "/api/external/virtual-bank-account"
        params = {}

        if wallet_id:
            params["wallet_id"] = wallet_id
        if customer_id:
            params["customer_id"] = customer_id

        if params:
            endpoint += "?" + urlencode(params)

        return self.client.make_request("GET", endpoint)

    def get(self, vba_id: str) -> Dict[str, Any]:
        """
        Get a specific virtual bank account.

        Args:
            vba_id: Virtual bank account ID

        Returns:
            API response containing virtual bank account data
        """
        if not vba_id:
            raise ValueError("Virtual bank account ID is required")

        return self.client.make_request("GET", f"/api/external/virtual-bank-account/{vba_id}")

    def close(self, vba_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Close a virtual bank account.

        Args:
            vba_id: Virtual bank account ID
            reason: Optional reason for closing

        Returns:
            API response
        """
        if not vba_id:
            raise ValueError("Virtual bank account ID is required")

        data = {}
        if reason is not None:
            data["reason"] = reason

        return self.client.make_request(
            "POST", f"/api/external/virtual-bank-account/{vba_id}/close", data
        )

    def get_identification_type(
        self,
        customer_id: Optional[str] = None,
        country: Optional[str] = None,
        type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get identification type requirements for virtual bank accounts.

        Args:
            customer_id: Customer ID (if provided, country and type not needed)
            country: Country code (required if customer_id not provided)
            type: Customer type (required if customer_id not provided)

        Returns:
            API response containing identification type requirements
        """
        if not customer_id and (not country or not type):
            raise ValueError("Either customer_id or both country and type are required")

        endpoint = "/api/external/virtual-bank-account/identification-type"
        params = {}

        if customer_id:
            params["customer_id"] = customer_id
        else:
            # Validation above ensures country and type are set
            params["country"] = country  # type: ignore[assignment]
            params["type"] = type  # type: ignore[assignment]

        endpoint += "?" + urlencode(params)

        return self.client.make_request("GET", endpoint)
