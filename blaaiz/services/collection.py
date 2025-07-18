"""
Collection Service
"""

from typing import Dict, Any


class CollectionService:
    """Service for managing collections."""

    def __init__(self, client):
        self.client = client

    def initiate(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a collection.

        Args:
            collection_data: Collection information

        Returns:
            API response containing collection data
        """
        required_fields = ["method", "amount", "wallet_id"]

        for field in required_fields:
            if field not in collection_data or not collection_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/collection", collection_data)

    def initiate_crypto(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a crypto collection.

        Args:
            crypto_data: Crypto collection information

        Returns:
            API response containing crypto collection data
        """
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

    def get_crypto_networks(self) -> Dict[str, Any]:
        """
        Get available crypto networks.

        Returns:
            API response containing crypto networks
        """
        return self.client.make_request("GET", "/api/external/collection/crypto/networks")
