"""
Transaction Service
"""

from typing import Dict, Any, Optional


class TransactionService:
    """Service for managing transactions."""

    def __init__(self, client):
        self.client = client

    def list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List transactions.

        Args:
            filters: Optional filters to apply

        Returns:
            API response containing list of transactions
        """
        if filters is None:
            filters = {}

        return self.client.make_request("POST", "/api/external/transaction", filters)

    def get(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get a specific transaction.

        Args:
            transaction_id: Transaction ID

        Returns:
            API response containing transaction data
        """
        if not transaction_id:
            raise ValueError("Transaction ID is required")

        return self.client.make_request("GET", f"/api/external/transaction/{transaction_id}")
