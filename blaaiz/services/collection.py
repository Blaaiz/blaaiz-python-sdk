"""
Collection Service
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode


class CollectionService:
    """Service for managing collections."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def initiate(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a collection.

        Args:
            collection_data: Collection information. Requires ``method``
                (``open_banking`` or ``card``), ``amount`` and ``wallet_id``.
                An optional ``merchant_reference`` (max 255, unique per business)
                is forwarded verbatim.

        Returns:
            API response containing collection data
        """
        required_fields = ["method", "amount", "wallet_id"]

        for field in required_fields:
            if field not in collection_data or not collection_data[field]:
                raise ValueError(f"{field} is required")

        # Card collections need the customer and the card details up front.
        if collection_data["method"] == "card":
            card_fields = ["customer_id", "card_holder_name", "card_number", "expiry", "cvc"]
            for field in card_fields:
                if field not in collection_data or not collection_data[field]:
                    raise ValueError(f"{field} is required for card method")

        return self.client.make_request("POST", "/api/external/collection", collection_data)

    def initiate_crypto(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a crypto collection.

        Args:
            crypto_data: Crypto collection information. Requires ``amount``,
                ``wallet_id``, ``network`` and ``token``.

        Returns:
            API response containing crypto collection data
        """
        required_fields = ["amount", "wallet_id", "network", "token"]

        for field in required_fields:
            if not crypto_data or field not in crypto_data or not crypto_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/collection/crypto", crypto_data)

    def attach_customer(self, attach_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attach a customer to a collection.

        Args:
            attach_data: Customer attachment information

        Returns:
            API response
        """
        required_fields = ["customer_id", "transaction_id"]

        for field in required_fields:
            if field not in attach_data or not attach_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request(
            "POST", "/api/external/collection/attach-customer", attach_data
        )

    def get_crypto_networks(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get available crypto networks.

        Args:
            filters: Optional query parameters. Supported key ``transaction_type``
                (``collection`` or ``payout``).

        Returns:
            API response containing crypto networks
        """
        endpoint = "/api/external/collection/crypto/networks"
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

    def initiate_interac_money_request(self, interac_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request an Interac transfer from a payer.

        Args:
            interac_data: Money request information. Requires ``amount`` and
                ``email``.

        Returns:
            API response
        """
        required_fields = ["amount", "email"]

        for field in required_fields:
            if not interac_data or field not in interac_data or not interac_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request(
            "POST", "/api/external/collection/interac-money-request", interac_data
        )

    def accept_interac_money_request(self, interac_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accept an Interac transfer into your business wallet.

        Args:
            interac_data: Interac money request data containing reference_number

        Returns:
            API response
        """
        required_fields = ["reference_number"]

        for field in required_fields:
            if field not in interac_data or not interac_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request(
            "POST", "/api/external/collection/accept-interac-money-request", interac_data
        )
