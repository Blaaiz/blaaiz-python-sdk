"""
Wallet Service
"""

from typing import Dict, Any


class WalletService:
    """Service for managing wallets."""
    
    def __init__(self, client):
        self.client = client
    
    def list(self) -> Dict[str, Any]:
        """
        List all wallets.
        
        Returns:
            API response containing list of wallets
        """
        return self.client.make_request('GET', '/api/external/wallet')
    
    def get(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get a specific wallet.
        
        Args:
            wallet_id: Wallet ID
            
        Returns:
            API response containing wallet data
        """
        if not wallet_id:
            raise ValueError("Wallet ID is required")
        
        return self.client.make_request('GET', f'/api/external/wallet/{wallet_id}')