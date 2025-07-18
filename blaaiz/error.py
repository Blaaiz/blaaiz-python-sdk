"""
Blaaiz Error Classes
"""


class BlaaizError(Exception):
    """Base exception class for Blaaiz API errors."""
    
    def __init__(self, message: str, status: int = None, code: str = None):
        """
        Initialize a Blaaiz error.
        
        Args:
            message: Error message
            status: HTTP status code
            code: Error code from API
        """
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
    
    def __str__(self):
        if self.status and self.code:
            return f"BlaaizError({self.status}, {self.code}): {self.message}"
        elif self.status:
            return f"BlaaizError({self.status}): {self.message}"
        else:
            return f"BlaaizError: {self.message}"
    
    def __repr__(self):
        return f"BlaaizError(message='{self.message}', status={self.status}, code='{self.code}')"