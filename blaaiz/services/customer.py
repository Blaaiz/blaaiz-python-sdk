"""
Customer Service
"""

import base64
import os
import tempfile
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Union
from ..error import BlaaizError


class CustomerService:
    """Service for managing customers."""

    def __init__(self, client):
        self.client = client

    def create(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer.

        Args:
            customer_data: Customer information

        Returns:
            API response containing customer data
        """
        required_fields = [
            "first_name",
            "last_name",
            "type",
            "email",
            "country",
            "id_type",
            "id_number",
        ]

        for field in required_fields:
            if field not in customer_data or not customer_data[field]:
                raise ValueError(f"{field} is required")

        if customer_data["type"] == "business" and not customer_data.get("business_name"):
            raise ValueError("business_name is required when type is business")

        return self.client.make_request("POST", "/api/external/customer", customer_data)

    def list(self) -> Dict[str, Any]:
        """
        List all customers.

        Returns:
            API response containing list of customers
        """
        return self.client.make_request("GET", "/api/external/customer")

    def get(self, customer_id: str) -> Dict[str, Any]:
        """
        Get a specific customer.

        Args:
            customer_id: Customer ID

        Returns:
            API response containing customer data
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        return self.client.make_request("GET", f"/api/external/customer/{customer_id}")

    def update(self, customer_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a customer.

        Args:
            customer_id: Customer ID
            update_data: Updated customer information

        Returns:
            API response containing updated customer data
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        return self.client.make_request("PUT", f"/api/external/customer/{customer_id}", update_data)

    def add_kyc(self, customer_id: str, kyc_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add KYC data to a customer.

        Args:
            customer_id: Customer ID
            kyc_data: KYC information

        Returns:
            API response
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        return self.client.make_request(
            "POST", f"/api/external/customer/{customer_id}/kyc-data", kyc_data
        )

    def upload_files(self, customer_id: str, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload files to a customer.

        Args:
            customer_id: Customer ID
            file_data: File information

        Returns:
            API response
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        return self.client.make_request(
            "PUT", f"/api/external/customer/{customer_id}/files", file_data
        )

    def upload_file_complete(
        self, customer_id: str, file_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete file upload process (get presigned URL, upload file, associate with customer).

        Args:
            customer_id: Customer ID
            file_options: File upload options containing:
                - file: File content (bytes, str, or URL)
                - file_category: Category ('identity', 'proof_of_address', 'liveness_check')
                - filename: Optional filename
                - content_type: Optional content type

        Returns:
            API response with file upload result
        """
        if not customer_id:
            raise ValueError("Customer ID is required")

        if not file_options:
            raise ValueError("File options are required")

        file_content = file_options.get("file")
        file_category = file_options.get("file_category")
        filename = file_options.get("filename")
        content_type = file_options.get("content_type")

        if not file_content:
            raise ValueError("File is required")

        if not file_category:
            raise ValueError("file_category is required")

        if file_category not in ["identity", "proof_of_address", "liveness_check"]:
            raise ValueError(
                "file_category must be one of: identity, proof_of_address, liveness_check"
            )

        try:
            # Step 1: Get presigned URL
            presigned_response = self.client.make_request(
                "POST",
                "/api/external/file/get-presigned-url",
                {"customer_id": customer_id, "file_category": file_category},
            )

            presigned_url = presigned_response["data"]["data"]["url"]
            file_id = presigned_response["data"]["data"]["file_id"]

            # Step 2: Process file content
            file_buffer = self._process_file_content(file_content, content_type, filename)

            # Step 3: Upload to S3
            self._upload_to_s3(
                presigned_url,
                file_buffer["data"],
                file_buffer.get("content_type"),
                file_buffer.get("filename"),
            )

            # Step 4: Associate file with customer
            file_association = self.client.make_request(
                "PUT", f"/api/external/customer/{customer_id}/files", {"id_file": file_id}
            )

            return {**file_association, "file_id": file_id, "presigned_url": presigned_url}

        except Exception as e:
            raise BlaaizError(f"File upload failed: {str(e)}")

    def _process_file_content(
        self, file_content: Union[bytes, str], content_type: Optional[str], filename: Optional[str]
    ) -> Dict[str, Any]:
        """Process file content from various formats."""
        result = {"filename": filename, "content_type": content_type}

        if isinstance(file_content, bytes):
            result["data"] = file_content
        elif isinstance(file_content, str):
            if file_content.startswith("data:"):
                # Handle data URL
                parts = file_content.split(",")
                if len(parts) != 2:
                    raise ValueError("Invalid data URL format")

                header = parts[0]
                data = parts[1]

                # Extract content type from data URL
                if not content_type and ";" in header:
                    content_type = header.split(":")[1].split(";")[0]
                    result["content_type"] = content_type

                result["data"] = base64.b64decode(data)
            elif file_content.startswith(("http://", "https://")):
                # Handle URL - download file
                download_result = self._download_file(file_content)
                result.update(download_result)
            else:
                # Handle plain base64 string
                result["data"] = base64.b64decode(file_content)
        else:
            raise ValueError("File content must be bytes or string")

        return result

    def _download_file(self, url: str) -> Dict[str, Any]:
        """Download file from URL."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Blaaiz-Python-SDK/1.0.0"})

            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status >= 300:
                    raise BlaaizError(f"Failed to download file: HTTP {response.status}")

                file_data = response.read()
                content_type = response.headers.get("content-type")

                # Extract filename from URL or Content-Disposition
                filename = None
                content_disposition = response.headers.get("content-disposition")
                if content_disposition and "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[1].strip("\"'")

                if not filename:
                    filename = os.path.basename(url.split("?")[0])

                # Add extension based on content type if missing
                if filename and not os.path.splitext(filename)[1] and content_type:
                    ext = self._get_extension_from_content_type(content_type)
                    if ext:
                        filename += ext

                return {"data": file_data, "content_type": content_type, "filename": filename}

        except urllib.error.URLError as e:
            raise BlaaizError(f"File download failed: {str(e)}")
        except Exception as e:
            raise BlaaizError(f"File download failed: {str(e)}")

    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """Get file extension from content type."""
        mime_to_ext = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/bmp": ".bmp",
            "image/tiff": ".tiff",
            "application/pdf": ".pdf",
            "text/plain": ".txt",
            "application/msword": ".doc",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        }

        return mime_to_ext.get(content_type.split(";")[0])

    def _upload_to_s3(
        self,
        presigned_url: str,
        file_data: bytes,
        content_type: Optional[str],
        filename: Optional[str],
    ):
        """Upload file to S3 using presigned URL."""
        headers = {"Content-Length": str(len(file_data))}

        if content_type:
            headers["Content-Type"] = content_type

        if filename:
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        req = urllib.request.Request(presigned_url, data=file_data, headers=headers, method="PUT")

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status < 200 or response.status >= 300:
                    raise BlaaizError(f"S3 upload failed with status {response.status}")
        except urllib.error.URLError as e:
            raise BlaaizError(f"S3 upload request failed: {str(e)}")
        except Exception as e:
            raise BlaaizError(f"S3 upload failed: {str(e)}")
