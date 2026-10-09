"""
Signa ID Release Service
"""

import urllib.parse
from typing import Any, Dict, List, Optional

RELEASE_SCOPES: List[str] = ["identity", "id_document", "address", "document_images"]

BASE_PATH = "/api/external/signa-id"


class SignaIdService:
    """Service for Signa ID data releases and wallet verification status."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def create_release_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Signa ID release request. Requires an OAuth token with the
        ``signa-id:release`` scope.

        Args:
            request_data: Requires ``idempotency_key``, ``purpose``, ``scopes``
                (a non-empty list of identity, id_document, address or
                document_images) and ``origin``. ``reference`` is optional.

        Returns:
            API response containing the release and its ``request_token``
        """
        self._validate_release_request_data(request_data)

        return self.client.make_request("POST", f"{BASE_PATH}/release-requests", request_data)

    def exchange_release_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange the one-time code from the Signa web SDK for the released data.

        Args:
            code: Release code

        Returns:
            API response containing the release and the released data
        """
        if not code or not isinstance(code, str):
            raise ValueError("Release code is required")

        return self.client.make_request("POST", f"{BASE_PATH}/releases/exchange", {"code": code})

    def get_release(self, release_id: str) -> Dict[str, Any]:
        """
        Read a release again during its access window.

        Args:
            release_id: Release ID

        Returns:
            API response containing the release and its data (``None`` before
            the exchange or when access is not ACTIVE)
        """
        self._validate_release_id(release_id)

        return self.client.make_request("GET", f"{BASE_PATH}/releases/{self._encode(release_id)}")

    def get_release_document(self, release_id: str, document_id: str) -> Dict[str, Any]:
        """
        Get a 15-minute download link for one released document image.

        Args:
            release_id: Release ID
            document_id: Document ID

        Returns:
            API response containing ``url``, ``content_type`` and ``expires_at``
        """
        self._validate_release_id(release_id)
        if not document_id:
            raise ValueError("Document ID is required")

        return self.client.make_request(
            "GET",
            f"{BASE_PATH}/releases/{self._encode(release_id)}"
            f"/documents/{self._encode(document_id)}",
        )

    def get_wallet_status(self, address: str, chain_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Check whether a wallet belongs to a verified Signa ID. This endpoint
        needs no authentication and returns no personal data.

        Args:
            address: Wallet address
            chain_id: Optional chain ID

        Returns:
            API response with ``verified``, ``level``, ``country``,
            ``expires_at`` and ``attestations`` at the root of the body
        """
        if not address:
            raise ValueError("Wallet address is required")

        endpoint = f"/api/v1/signa-id/public/wallets/{self._encode(address)}/status"
        if chain_id is not None:
            endpoint = f"{endpoint}?{urllib.parse.urlencode({'chain_id': chain_id})}"

        return self.client.make_request("GET", endpoint)

    def _validate_release_request_data(self, request_data: Dict[str, Any]) -> None:
        if not isinstance(request_data, dict):
            raise ValueError("Release request data is required")

        for field in ("idempotency_key", "purpose", "scopes", "origin"):
            value = request_data.get(field)
            if value is None or value == "":
                raise ValueError(f"{field} is required")

        scopes = request_data["scopes"]
        if not isinstance(scopes, list) or len(scopes) == 0:
            raise ValueError("scopes must be a non-empty array")

        for scope in scopes:
            if scope not in RELEASE_SCOPES:
                raise ValueError(f"scopes must contain only: {', '.join(RELEASE_SCOPES)}")

    def _validate_release_id(self, release_id: str) -> None:
        if not release_id:
            raise ValueError("Release ID is required")

    def _encode(self, path_segment: str) -> str:
        return urllib.parse.quote(path_segment, safe="")
