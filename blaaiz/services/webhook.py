"""
Webhook Service
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Union


class WebhookService:
    """Service for managing webhooks."""

    def __init__(self, client):
        self.client = client

    def register(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register webhook URLs.

        Args:
            webhook_data: Webhook configuration

        Returns:
            API response
        """
        required_fields = ["collection_url", "payout_url"]

        for field in required_fields:
            if field not in webhook_data or not webhook_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/webhook", webhook_data)

    def get(self) -> Dict[str, Any]:
        """
        Get webhook configuration.

        Returns:
            API response containing webhook configuration
        """
        return self.client.make_request("GET", "/api/external/webhook")

    def update(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update webhook configuration.

        Args:
            webhook_data: Updated webhook configuration

        Returns:
            API response
        """
        return self.client.make_request("PUT", "/api/external/webhook", webhook_data)

    def replay(self, replay_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replay a webhook.

        Args:
            replay_data: Replay configuration

        Returns:
            API response
        """
        required_fields = ["transaction_id"]

        for field in required_fields:
            if field not in replay_data or not replay_data[field]:
                raise ValueError(f"{field} is required")

        return self.client.make_request("POST", "/api/external/webhook/replay", replay_data)

    def verify_signature(self, payload: Union[str, dict], signature: str, secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret

        Returns:
            True if signature is valid, False otherwise
        """
        if not payload:
            raise ValueError("Payload is required for signature verification")

        if not signature:
            raise ValueError("Signature is required for signature verification")

        if not secret:
            raise ValueError("Webhook secret is required for signature verification")

        # Convert payload to string if it's a dict
        if isinstance(payload, dict):
            payload_string = json.dumps(payload, separators=(",", ":"))
        else:
            payload_string = payload

        # Remove 'sha256=' prefix if present
        clean_signature = signature.replace("sha256=", "")

        # Create HMAC signature
        expected_signature = hmac.new(
            secret.encode("utf-8"), payload_string.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(clean_signature, expected_signature)

    def construct_event(
        self, payload: Union[str, dict], signature: str, secret: str
    ) -> Dict[str, Any]:
        """
        Construct and verify webhook event.

        Args:
            payload: Webhook payload
            signature: Webhook signature
            secret: Webhook secret

        Returns:
            Verified webhook event

        Raises:
            ValueError: If signature is invalid or payload cannot be parsed
        """
        if not self.verify_signature(payload, signature, secret):
            raise ValueError("Invalid webhook signature")

        try:
            if isinstance(payload, str):
                event = json.loads(payload)
            else:
                event = payload

            # Add verification metadata
            event["verified"] = True
            event["timestamp"] = self._get_current_timestamp()

            return event

        except json.JSONDecodeError:
            raise ValueError("Invalid webhook payload: unable to parse JSON")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.utcnow().isoformat() + "Z"
