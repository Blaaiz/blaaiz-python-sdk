"""
Flask Integration Example for Blaaiz Python SDK

This example demonstrates how to integrate the Blaaiz SDK into a Flask web application
for handling payments, collections, and customer management.
"""

from flask import Flask, request, jsonify, render_template_string
from blaaiz import Blaaiz, BlaaizError
import os
from datetime import datetime, timezone

app = Flask(__name__)

# Initialize Blaaiz SDK
blaaiz = Blaaiz(
    api_key=os.getenv("BLAAIZ_API_KEY", "your-api-key-here"),
    base_url=os.getenv("BLAAIZ_BASE_URL", "https://api-dev.blaaiz.com"),
)

# Webhook secret
WEBHOOK_SECRET = os.getenv("BLAAIZ_WEBHOOK_SECRET", "your-webhook-secret")

# Simple in-memory store for demo (use a proper database in production)
customers_db = {}
transactions_db = {}


@app.route("/")
def index():
    """Main page with API status and basic information."""

    is_connected = blaaiz.test_connection()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Blaaiz Flask Integration</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
            .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
            .endpoint { margin: 20px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #007bff; }
            .method { font-weight: bold; color: #007bff; }
        </style>
    </head>
    <body>
        <h1>Blaaiz Flask Integration Demo</h1>
        
        <div class="status {{ 'success' if is_connected else 'error' }}">
            <strong>API Status:</strong> {{ 'Connected' if is_connected else 'Disconnected' }}
        </div>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/status</code> - Check API connection status
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/customers</code> - Create a new customer
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/customers</code> - List all customers
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/customers/&lt;id&gt;</code> - Get customer by ID
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/collections</code> - Initiate a collection
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/payouts</code> - Initiate a payout
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/wallets</code> - List wallets
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/currencies</code> - List currencies
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/banks</code> - List banks
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/fees</code> - Calculate fees
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/webhooks/collection</code> - Collection webhook
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/webhooks/payout</code> - Payout webhook
        </div>
        
        <p><strong>Note:</strong> This is a demo application. Use proper authentication and validation in production.</p>
    </body>
    </html>
    """

    return render_template_string(html, is_connected=is_connected)


@app.route("/api/status", methods=["GET"])
def api_status():
    """Check API connection status."""

    is_connected = blaaiz.test_connection()

    return jsonify(
        {
            "connected": is_connected,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sdk_version": "1.0.5",
        }
    )


@app.route("/api/customers", methods=["POST"])
def create_customer():
    """Create a new customer."""

    try:
        data = request.get_json()

        # Validate required fields
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
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create customer using Blaaiz SDK
        customer = blaaiz.customers.create(data)
        customer_id = customer["data"]["data"]["id"]

        # Store in local database
        customers_db[customer_id] = {
            "id": customer_id,
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "blaaiz_response": customer["data"],
        }

        return (
            jsonify({"success": True, "customer_id": customer_id, "customer": customer["data"]}),
            201,
        )

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers", methods=["GET"])
def list_customers():
    """List all customers."""

    try:
        customers = blaaiz.customers.list()

        return jsonify({"success": True, "customers": customers["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/customers/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Get customer by ID."""

    try:
        customer = blaaiz.customers.get(customer_id)

        return jsonify({"success": True, "customer": customer["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/collections", methods=["POST"])
def create_collection():
    """Initiate a collection."""

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["method", "amount", "wallet_id"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create collection using Blaaiz SDK
        collection = blaaiz.collections.initiate(data)
        transaction_id = collection["data"]["transaction_id"]

        # Store in local database
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "type": "collection",
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "blaaiz_response": collection["data"],
        }

        return (
            jsonify(
                {
                    "success": True,
                    "transaction_id": transaction_id,
                    "collection": collection["data"],
                }
            ),
            201,
        )

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/payouts", methods=["POST"])
def create_payout():
    """Initiate a payout."""

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = [
            "wallet_id",
            "method",
            "from_amount",
            "from_currency_id",
            "to_currency_id",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create payout using Blaaiz SDK
        payout = blaaiz.payouts.initiate(data)
        transaction_id = payout["data"]["transaction"]["id"]

        # Store in local database
        transactions_db[transaction_id] = {
            "id": transaction_id,
            "type": "payout",
            "data": data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "blaaiz_response": payout["data"],
        }

        return (
            jsonify({"success": True, "transaction_id": transaction_id, "payout": payout["data"]}),
            201,
        )

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/wallets", methods=["GET"])
def list_wallets():
    """List all wallets."""

    try:
        wallets = blaaiz.wallets.list()

        return jsonify({"success": True, "wallets": wallets["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/currencies", methods=["GET"])
def list_currencies():
    """List all currencies."""

    try:
        currencies = blaaiz.currencies.list()

        return jsonify({"success": True, "currencies": currencies["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/banks", methods=["GET"])
def list_banks():
    """List all banks."""

    try:
        banks = blaaiz.banks.list()

        return jsonify({"success": True, "banks": banks["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/fees", methods=["POST"])
def calculate_fees():
    """Calculate fees for a transaction."""

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["from_currency_id", "to_currency_id", "from_amount"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Calculate fees using Blaaiz SDK
        fees = blaaiz.fees.get_breakdown(data)

        return jsonify({"success": True, "fees": fees["data"]})

    except BlaaizError as e:
        return (
            jsonify(
                {
                    "error": "Blaaiz API Error",
                    "message": e.message,
                    "status": e.status,
                    "code": e.code,
                }
            ),
            e.status or 400,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhooks/collection", methods=["POST"])
def handle_collection_webhook():
    """Handle collection webhook notifications."""

    signature = request.headers.get("x-blaaiz-signature")
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, WEBHOOK_SECRET)

        transaction_id = event.get("transaction_id")
        status = event.get("status")

        app.logger.info(f"Collection webhook received: {transaction_id} - {status}")

        # Update local database
        if transaction_id in transactions_db:
            transactions_db[transaction_id]["last_webhook"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "event": event,
            }

        # Process the collection based on status
        if status == "SUCCESSFUL":
            app.logger.info(f"Collection successful: {transaction_id}")
            # Handle successful collection
            # Update user account, send notifications, etc.

        elif status == "FAILED":
            app.logger.warning(f"Collection failed: {transaction_id}")
            # Handle failed collection
            # Notify user, log failure, etc.

        elif status == "PENDING":
            app.logger.info(f"Collection pending: {transaction_id}")
            # Monitor pending collection

        return (
            jsonify({"received": True, "transaction_id": transaction_id, "status": "processed"}),
            200,
        )

    except ValueError as e:
        app.logger.error(f"Collection webhook verification failed: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        app.logger.error(f"Collection webhook processing error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500


@app.route("/webhooks/payout", methods=["POST"])
def handle_payout_webhook():
    """Handle payout webhook notifications."""

    signature = request.headers.get("x-blaaiz-signature")
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, WEBHOOK_SECRET)

        transaction_id = event.get("transaction_id")
        status = event.get("status")

        app.logger.info(f"Payout webhook received: {transaction_id} - {status}")

        # Update local database
        if transaction_id in transactions_db:
            transactions_db[transaction_id]["last_webhook"] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "event": event,
            }

        # Process the payout based on status
        if status == "SUCCESSFUL":
            app.logger.info(f"Payout successful: {transaction_id}")
            # Handle successful payout
            # Update user account, send notifications, etc.

        elif status == "FAILED":
            app.logger.warning(f"Payout failed: {transaction_id}")
            # Handle failed payout
            # Notify user, log failure, possibly refund wallet, etc.

        elif status == "PENDING":
            app.logger.info(f"Payout pending: {transaction_id}")
            # Monitor pending payout

        return (
            jsonify({"received": True, "transaction_id": transaction_id, "status": "processed"}),
            200,
        )

    except ValueError as e:
        app.logger.error(f"Payout webhook verification failed: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        app.logger.error(f"Payout webhook processing error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500


@app.route("/api/transactions", methods=["GET"])
def list_transactions():
    """List local transactions (for demo purposes)."""

    return jsonify({"success": True, "transactions": list(transactions_db.values())})


@app.route("/api/customers/local", methods=["GET"])
def list_local_customers():
    """List local customers (for demo purposes)."""

    return jsonify({"success": True, "customers": list(customers_db.values())})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("Blaaiz Flask Integration Demo")
    print("=" * 40)

    # Check connection
    if blaaiz.test_connection():
        print("✓ Connected to Blaaiz API")
    else:
        print("✗ Failed to connect to Blaaiz API")
        print("  Please check your API key and network connection")

    print("\nStarting Flask application...")
    print("Open your browser to: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /api/status - Check API status")
    print("  POST /api/customers - Create customer")
    print("  GET  /api/customers - List customers")
    print("  POST /api/collections - Create collection")
    print("  POST /api/payouts - Create payout")
    print("  GET  /api/wallets - List wallets")
    print("  GET  /api/currencies - List currencies")
    print("  GET  /api/banks - List banks")
    print("  POST /api/fees - Calculate fees")
    print("\nWebhook Endpoints:")
    print("  POST /webhooks/collection - Collection webhook")
    print("  POST /webhooks/payout - Payout webhook")

    # Set up logging
    import logging

    logging.basicConfig(level=logging.INFO)

    app.run(host="0.0.0.0", port=5000, debug=True)
