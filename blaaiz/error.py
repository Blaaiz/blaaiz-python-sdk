"""
Blaaiz Error Classes
"""

from typing import Optional


class BlaaizError(Exception):
    """Base exception class for Blaaiz API errors."""

    def __init__(self, message: str, status: Optional[int] = None, code: Optional[str] = None):
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

    def __str__(self) -> str:
        if self.status and self.code:
            return f"BlaaizError({self.status}, {self.code}): {self.message}"
        elif self.status:
            return f"BlaaizError({self.status}): {self.message}"
        else:
            return f"BlaaizError: {self.message}"

    def __repr__(self) -> str:
        return f"BlaaizError(message='{self.message}', status={self.status}, code='{self.code}')"
