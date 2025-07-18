"""
Fees Service
"""

from typing import Dict, Any


class FeesService:
    """Service for managing fees."""
    
    def __init__(self, client):
        self.client = client
    
    def get_breakdown(self, fee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get fee breakdown.
        
        Args:
            fee_data: Fee calculation data
            
        Returns:
            API response containing fee breakdown
        """
        required_fields = ['from_currency_id', 'to_currency_id', 'from_amount']
        
        for field in required_fields:
            if field not in fee_data or not fee_data[field]:
                raise ValueError(f"{field} is required")
        
        return self.client.make_request('POST', '/api/external/fees/breakdown', fee_data)