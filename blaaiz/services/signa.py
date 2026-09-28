"""
Signa Merchant KYC/KYB Session Service
"""

import urllib.parse
from typing import Any, Dict, List, Optional

REQUIREMENTS: List[str] = ["DOCUMENTS", "SELFIE", "FACE_MATCH", "PROOF_OF_ADDRESS"]

DOCUMENT_TYPES: List[str] = [
    "PASSPORT",
    "ID_CARD",
    "DRIVERS",
    "RESIDENCE_PERMIT",
    "UTILITY_BILL",
    "BANK_STATEMENT",
    "SELFIE",
]

CONTENT_TYPES: List[str] = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
]

BASE_PATH = "/api/external/compliance/kyc/sessions"


class SignaService:
    """Service for managing Signa merchant KYC/KYB verification sessions."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Signa verification session.

        Args:
            session_data: Session information. Requires ``customer_reference``
                (max 100), ``idempotency_key`` (max 100; a repeated key
                replays the same session) and ``requirements`` (1-4 distinct
                values from DOCUMENTS, SELFIE, FACE_MATCH, PROOF_OF_ADDRESS).
                ``fulfilment_mode`` (HOSTED or HEADLESS) and ``applicant``
                (first_name, last_name, dob, country) are optional.

        Returns:
            API response containing session data
        """
        self._validate_session_data(session_data)

        return self.client.make_request("POST", BASE_PATH, session_data)

    def list_sessions(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List Signa sessions, optionally paginated.

        Args:
            filters: Optional query parameters. Supported keys are ``limit``
                and ``offset``.

        Returns:
            API response containing sessions, total, limit and offset
        """
        endpoint = BASE_PATH
        if filters:
            params = {key: value for key, value in filters.items() if value is not None}
            if params:
                endpoint = f"{BASE_PATH}?{urllib.parse.urlencode(params)}"
        return self.client.make_request("GET", endpoint)

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get a specific Signa session.

        Args:
            session_id: Session ID

        Returns:
            API response containing session data
        """
        self._validate_session_id(session_id)

        return self.client.make_request("GET", f"{BASE_PATH}/{self._encode(session_id)}")

    def submit_session(self, session_id: str) -> Dict[str, Any]:
        """
        Submit a session for verification. HEADLESS sessions only.

        Args:
            session_id: Session ID

        Returns:
            API response containing session data
        """
        self._validate_session_id(session_id)

        return self.client.make_request("POST", f"{BASE_PATH}/{self._encode(session_id)}/submit")

    def cancel_session(self, session_id: str) -> Dict[str, Any]:
        """
        Cancel a Signa session.

        Args:
            session_id: Session ID

        Returns:
            API response containing session data
        """
        self._validate_session_id(session_id)

        return self.client.make_request("POST", f"{BASE_PATH}/{self._encode(session_id)}/cancel")

    def create_document_upload_url(
        self, session_id: str, upload_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get a short-lived upload URL for a session document.

        Args:
            session_id: Session ID
            upload_data: Requires ``file_name`` (max 128; letters, numbers,
                spaces, dashes and underscores; ends .jpg/.jpeg/.png/.webp/.pdf)
                and ``id_doc_type`` (PASSPORT, ID_CARD, DRIVERS,
                RESIDENCE_PERMIT, UTILITY_BILL, BANK_STATEMENT or SELFIE).

        Returns:
            API response containing ``url``, ``file_name`` and the ``headers``
            that must be sent verbatim with the direct PUT (they are part of
            the URL's signature)
        """
        self._validate_session_id(session_id)
        self._validate_document_upload_url_data(upload_data)

        return self.client.make_request(
            "POST",
            f"{BASE_PATH}/{self._encode(session_id)}/documents/upload-url",
            upload_data,
        )

    def upload_session_document(
        self, session_id: str, document_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register a document against a session. HEADLESS sessions only.

        Args:
            session_id: Session ID
            document_data: Requires ``filename`` (max 191), ``content_type``
                (image/jpeg, image/png, image/webp or application/pdf),
                ``id_doc_type`` and ``country`` (ISO 3166-1 alpha-3). Provide
                exactly one of ``file_name`` (staged, from
                ``create_document_upload_url``) or ``content_base64``
                (inline; only for very small files, because the API can
                reject request bodies over roughly 8 KB).

        Returns:
            API response containing session data
        """
        self._validate_session_id(session_id)
        self._validate_document_data(document_data)

        return self.client.make_request(
            "POST",
            f"{BASE_PATH}/{self._encode(session_id)}/documents",
            document_data,
        )

    def issue_verification_link(self, session_id: str) -> Dict[str, Any]:
        """
        Issue or rotate a hosted verification link. HOSTED sessions only.

        Args:
            session_id: Session ID

        Returns:
            API response containing verification_link and link_expires_at
        """
        self._validate_session_id(session_id)

        return self.client.make_request(
            "POST", f"{BASE_PATH}/{self._encode(session_id)}/verification-link"
        )

    # Short aliases mirror the create/list/get style used by the other SDK resources.
    def create(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.create_session(session_data)

    def list(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.list_sessions(filters)

    def get(self, session_id: str) -> Dict[str, Any]:
        return self.get_session(session_id)

    def submit(self, session_id: str) -> Dict[str, Any]:
        return self.submit_session(session_id)

    def cancel(self, session_id: str) -> Dict[str, Any]:
        return self.cancel_session(session_id)

    def upload_document(self, session_id: str, document_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.upload_session_document(session_id, document_data)

    def _validate_session_data(self, session_data: Dict[str, Any]) -> None:
        if not isinstance(session_data, dict):
            raise ValueError("Session data is required")

        for field in ("customer_reference", "idempotency_key", "requirements"):
            value = session_data.get(field)
            if value is None or value == "":
                raise ValueError(f"{field} is required")

        requirements = session_data["requirements"]
        if not isinstance(requirements, list) or len(requirements) == 0:
            raise ValueError("requirements must be a non-empty array")

        for requirement in requirements:
            if not isinstance(requirement, str) or requirement.upper() not in REQUIREMENTS:
                raise ValueError(f"requirements must contain only: {', '.join(REQUIREMENTS)}")

    def _validate_document_upload_url_data(self, upload_data: Dict[str, Any]) -> None:
        self._validate_document_data_shape(upload_data, ["file_name", "id_doc_type"])

        id_doc_type = upload_data.get("id_doc_type")
        if not isinstance(id_doc_type, str) or id_doc_type.upper() not in DOCUMENT_TYPES:
            raise ValueError(f"id_doc_type must be one of: {', '.join(DOCUMENT_TYPES)}")

    def _validate_document_data(self, document_data: Dict[str, Any]) -> None:
        self._validate_document_data_shape(
            document_data, ["filename", "content_type", "id_doc_type", "country"]
        )

        content_type = document_data.get("content_type")
        if not isinstance(content_type, str) or content_type.lower() not in CONTENT_TYPES:
            raise ValueError(f"content_type must be one of: {', '.join(CONTENT_TYPES)}")

        id_doc_type = document_data.get("id_doc_type")
        if not isinstance(id_doc_type, str) or id_doc_type.upper() not in DOCUMENT_TYPES:
            raise ValueError(f"id_doc_type must be one of: {', '.join(DOCUMENT_TYPES)}")

        has_staged_file = (
            isinstance(document_data.get("file_name"), str) and document_data["file_name"] != ""
        )
        has_inline_content = (
            isinstance(document_data.get("content_base64"), str)
            and document_data["content_base64"] != ""
        )

        if has_staged_file == has_inline_content:
            raise ValueError("Provide exactly one of file_name or content_base64")

    def _validate_document_data_shape(self, data: Dict[str, Any], fields: List[str]) -> None:
        if not isinstance(data, dict):
            raise ValueError("Document data is required")

        for field in fields:
            value = data.get(field)
            if value is None or value == "":
                raise ValueError(f"{field} is required")

    def _validate_session_id(self, session_id: str) -> None:
        if not session_id:
            raise ValueError("Session ID is required")

    def _encode(self, session_id: str) -> str:
        return urllib.parse.quote(session_id, safe="")
