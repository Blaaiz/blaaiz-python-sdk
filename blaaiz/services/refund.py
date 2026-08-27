"""
Refund Service
"""

from typing import Dict, Any


class RefundService:
    """Service for managing refunds."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def initiate(self, refund_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a refund for a transaction.

        Args:
            refund_data: Refund information. Requires ``transaction_id``.
                ``reason`` (max 250) and ``reference`` (max 100) are optional.

        Returns:
            API response containing refund data
        """
        if not refund_data or not refund_data.get("transaction_id"):
            raise ValueError("transaction_id is required")

        return self.client.make_request("POST", "/api/external/refund", refund_data)

    def get(self, refund_id: str) -> Dict[str, Any]:
        """
        Get a specific refund.

        Args:
            refund_id: Refund ID

        Returns:
            API response containing refund data
        """
        if not refund_id:
            raise ValueError("Refund ID is required")

        return self.client.make_request("GET", f"/api/external/refund/{refund_id}")
