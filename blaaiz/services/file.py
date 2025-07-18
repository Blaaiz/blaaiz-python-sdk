"""
File Service
"""

from typing import Dict, Any


class FileService:
    """Service for managing files."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def get_presigned_url(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get presigned URL for file upload.

        Args:
            file_data: File upload information

        Returns:
            API response containing presigned URL
        """
        required_fields = ["customer_id", "file_category"]

        for field in required_fields:
            if field not in file_data or not file_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/file/get-presigned-url", file_data)
