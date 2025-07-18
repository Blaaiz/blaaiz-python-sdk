"""
Webhook Server Example for Blaaiz Python SDK

This example shows how to set up a webhook server using Flask
to handle Blaaiz webhook notifications with signature verification.
"""

from flask import Flask, request, jsonify
from blaaiz import Blaaiz
import os
import json

app = Flask(__name__)

# Initialize Blaaiz SDK
blaaiz = Blaaiz(os.getenv("BLAAIZ_API_KEY", "your-api-key-here"))

# Webhook secret (get this from your Blaaiz dashboard)
WEBHOOK_SECRET = os.getenv("BLAAIZ_WEBHOOK_SECRET", "your-webhook-secret")


@app.route("/webhooks/collection", methods=["POST"])
def handle_collection_webhook():
    """Handle collection webhook notifications."""

    signature = request.headers.get("x-blaaiz-signature")
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, WEBHOOK_SECRET)

        print(f"✓ Verified collection webhook: {event['transaction_id']}")
        print(f"  Status: {event.get('status', 'N/A')}")
        print(f"  Amount: {event.get('amount', 'N/A')}")
        print(f"  Currency: {event.get('currency', 'N/A')}")
        print(f"  Verified: {event['verified']}")
        print(f"  Timestamp: {event['timestamp']}")

        # Process the collection based on status
        if event.get("status") == "SUCCESSFUL":
            print("  → Collection successful - updating records...")
            # Update your database
            # Send notifications
            # Process the successful collection

        elif event.get("status") == "FAILED":
            print("  → Collection failed - handling failure...")
            # Handle failed collection
            # Notify customer
            # Log failure

        elif event.get("status") == "PENDING":
            print("  → Collection pending - monitoring...")
            # Monitor pending collection

        return (
            jsonify(
                {
                    "received": True,
                    "transaction_id": event.get("transaction_id"),
                    "status": "processed",
                }
            ),
            200,
        )

    except ValueError as e:
        print(f"✗ Collection webhook verification failed: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print(f"✗ Collection webhook processing error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500


@app.route("/webhooks/payout", methods=["POST"])
def handle_payout_webhook():
    """Handle payout webhook notifications."""

    signature = request.headers.get("x-blaaiz-signature")
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, WEBHOOK_SECRET)

        print(f"✓ Verified payout webhook: {event['transaction_id']}")
        print(f"  Status: {event.get('status', 'N/A')}")
        print(f"  Recipient: {event.get('recipient', {}).get('account_name', 'N/A')}")
        print(f"  Amount: {event.get('amount', 'N/A')}")
        print(f"  Verified: {event['verified']}")
        print(f"  Timestamp: {event['timestamp']}")

        # Process the payout based on status
        if event.get("status") == "SUCCESSFUL":
            print("  → Payout successful - updating records...")
            # Update your database
            # Send notifications
            # Process the successful payout

        elif event.get("status") == "FAILED":
            print("  → Payout failed - handling failure...")
            # Handle failed payout
            # Notify customer
            # Log failure
            # Possibly refund wallet

        elif event.get("status") == "PENDING":
            print("  → Payout pending - monitoring...")
            # Monitor pending payout

        return (
            jsonify(
                {
                    "received": True,
                    "transaction_id": event.get("transaction_id"),
                    "status": "processed",
                }
            ),
            200,
        )

    except ValueError as e:
        print(f"✗ Payout webhook verification failed: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        print(f"✗ Payout webhook processing error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500


@app.route("/webhooks/test", methods=["POST"])
def test_webhook():
    """Test endpoint to verify webhook setup."""

    signature = request.headers.get("x-blaaiz-signature")
    payload = request.get_data(as_text=True)

    print(f"Test webhook received:")
    print(f"  Headers: {dict(request.headers)}")
    print(f"  Payload: {payload}")

    if signature:
        try:
            is_valid = blaaiz.webhooks.verify_signature(payload, signature, WEBHOOK_SECRET)
            print(f"  Signature valid: {is_valid}")
        except Exception as e:
            print(f"  Signature verification error: {str(e)}")

    return jsonify({"received": True, "message": "Test webhook processed successfully"}), 200


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "blaaiz-webhook-server",
                "api_connected": blaaiz.test_connection(),
            }
        ),
        200,
    )


@app.route("/webhooks/manual-verify", methods=["POST"])
def manual_verify():
    """Manual webhook verification for testing."""

    data = request.get_json()
    payload = data.get("payload")
    signature = data.get("signature")

    try:
        # Method 1: Manual verification
        is_valid = blaaiz.webhooks.verify_signature(payload, signature, WEBHOOK_SECRET)

        # Method 2: Construct event
        event = blaaiz.webhooks.construct_event(payload, signature, WEBHOOK_SECRET)

        return (
            jsonify(
                {
                    "signature_valid": is_valid,
                    "event_constructed": True,
                    "event_verified": event.get("verified", False),
                    "event_timestamp": event.get("timestamp"),
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"signature_valid": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500


def register_webhooks():
    """Register webhook URLs with Blaaiz."""

    try:
        # Replace with your actual webhook URLs
        webhook_urls = {
            "collection_url": "https://your-domain.com/webhooks/collection",
            "payout_url": "https://your-domain.com/webhooks/payout",
        }

        result = blaaiz.webhooks.register(webhook_urls)
        print(f"✓ Webhooks registered successfully: {result}")

    except Exception as e:
        print(f"✗ Failed to register webhooks: {str(e)}")


if __name__ == "__main__":
    print("Blaaiz Webhook Server")
    print("=" * 30)

    # Check connection
    if blaaiz.test_connection():
        print("✓ Connected to Blaaiz API")
    else:
        print("✗ Failed to connect to Blaaiz API")

    # Uncomment to register webhooks
    # register_webhooks()

    print(f"Starting webhook server on port 5000...")
    print(f"Collection webhook: http://localhost:5000/webhooks/collection")
    print(f"Payout webhook: http://localhost:5000/webhooks/payout")
    print(f"Test webhook: http://localhost:5000/webhooks/test")
    print(f"Health check: http://localhost:5000/health")

    app.run(host="0.0.0.0", port=5000, debug=True)
