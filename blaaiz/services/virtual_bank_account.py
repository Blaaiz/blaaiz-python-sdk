"""
Virtual Bank Account Service
"""

from typing import Dict, Any, Optional


class VirtualBankAccountService:
    """Service for managing virtual bank accounts."""
    
    def __init__(self, client):
        self.client = client
    
    def create(self, vba_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a virtual bank account.
        
        Args:
            vba_data: Virtual bank account information
            
        Returns:
            API response containing virtual bank account data
        """
        required_fields = ['wallet_id']
        
        for field in required_fields:
            if field not in vba_data or not vba_data[field]:
                raise ValueError(f"{field} is required")
        
        return self.client.make_request('POST', '/api/external/virtual-bank-account', vba_data)
    
    def list(self, wallet_id: Optional[str] = None) -> Dict[str, Any]:
        """
        List virtual bank accounts.
        
        Args:
            wallet_id: Optional wallet ID to filter by
            
        Returns:
            API response containing list of virtual bank accounts
        """
        params = f'?wallet_id={wallet_id}' if wallet_id else ''
        return self.client.make_request('GET', f'/api/external/virtual-bank-account{params}')
    
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
        
        return self.client.make_request('GET', f'/api/external/virtual-bank-account/{vba_id}')