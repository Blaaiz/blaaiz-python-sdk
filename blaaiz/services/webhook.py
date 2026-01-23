"""
Webhook Service
"""

import hmac
import hashlib
import json
from typing import Dict, Any


class WebhookService:
    """Service for managing webhooks."""

    def __init__(self, client: Any) -> None:
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

    def simulate_interac_webhook(self, simulate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate an Interac webhook (non-production only).

        Sends a mock Interac collection webhook to your configured collection_url.
        Only available outside production; returns 400 in production.

        Args:
            simulate_data: Simulation data

        Returns:
            API response
        """
        return self.client.make_request(
            "POST", "/api/external/mock/simulate-webhook/interac", simulate_data
        )

    def verify_signature(self, raw_body: str, signature: str, timestamp: str, secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            raw_body: Raw webhook payload string
            signature: Webhook signature from x-blaaiz-signature header
            timestamp: Timestamp from x-blaaiz-timestamp header
            secret: Webhook secret (your API secret key)

        Returns:
            True if signature is valid, False otherwise
        """
        if not raw_body:
            raise ValueError("Payload is required for signature verification")

        if not signature:
            raise ValueError("Signature is required for signature verification")

        if not secret:
            raise ValueError("Webhook secret is required for signature verification")

        if not timestamp:
            raise ValueError("Timestamp is required for signature verification")

        # Create the signature string: timestamp.payload
        signed = f"{timestamp}.{raw_body}"

        # Generate the expected signature using HMAC SHA-256
        expected_signature = hmac.new(
            secret.encode("utf-8"), signed.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature.lower())

    def construct_event(
        self, payload: str, signature: str, timestamp: str, secret: str
    ) -> Dict[str, Any]:
        """
        Construct and verify webhook event.

        Args:
            payload: Raw webhook payload string
            signature: Webhook signature from x-blaaiz-signature header
            timestamp: Timestamp from x-blaaiz-timestamp header
            secret: Webhook secret (your API secret key)

        Returns:
            Verified webhook event with 'verified' and 'timestamp' metadata

        Raises:
            ValueError: If signature is invalid or payload cannot be parsed
        """
        if not self.verify_signature(payload, signature, timestamp, secret):
            raise ValueError("Invalid webhook signature")

        try:
            event = json.loads(payload)

            # Add verification metadata
            event["verified"] = True
            event["timestamp"] = self._get_current_timestamp()

            return event

        except json.JSONDecodeError:
            raise ValueError("Invalid webhook payload: unable to parse JSON")

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
