"""
Swap Service
"""

from typing import Dict, Any


class SwapService:
    """Service for swapping between business wallets."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def initiate(self, swap_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate a swap between two business wallets.

        Args:
            swap_data: Swap information. Requires ``from_business_wallet_id``,
                ``to_business_wallet_id`` and ``amount``. An optional
                ``amount_type`` (``from`` or ``to``, default ``from``) selects
                which side ``amount`` applies to.

        Returns:
            API response containing swap data
        """
        required_fields = ["from_business_wallet_id", "to_business_wallet_id", "amount"]

        for field in required_fields:
            if field not in swap_data or not swap_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/swap", swap_data)
