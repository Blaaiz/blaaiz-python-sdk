# Blaaiz Python SDK Examples

This directory contains comprehensive examples demonstrating how to use the Blaaiz Python SDK in various scenarios.

## Prerequisites

Before running the examples, make sure you have:

1. **Python 3.7+** installed
2. **Blaaiz API Key** from your Blaaiz dashboard
3. **Webhook Secret** (for webhook examples)

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install just the SDK:

```bash
pip install blaaiz-python-sdk
```

## Environment Setup

Set up your environment variables:

```bash
export BLAAIZ_API_KEY="your-api-key-here"
export BLAAIZ_WEBHOOK_SECRET="your-webhook-secret"
export BLAAIZ_BASE_URL="https://api-dev.blaaiz.com"  # Optional
```

Or create a `.env` file:

```
BLAAIZ_API_KEY=your-api-key-here
BLAAIZ_WEBHOOK_SECRET=your-webhook-secret
BLAAIZ_BASE_URL=https://api-dev.blaaiz.com
```

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

Demonstrates fundamental SDK operations:
- Testing API connection
- Listing currencies and banks
- Creating customers
- Calculating fees

```bash
python basic_usage.py
```

### 2. Complete Workflows (`complete_workflows.py`)

Shows end-to-end workflows:
- Complete payout process (customer + fees + payout)
- Complete collection process (customer + VBA + collection)
- Interac payouts
- Crypto collections

```bash
python complete_workflows.py
```

### 3. File Upload (`file_upload.py`)

Demonstrates various file upload methods:
- Upload from local files
- Upload from base64 strings
- Upload from data URLs
- Upload from public URLs
- Manual 3-step upload process
- Batch file uploads

```bash
python file_upload.py
```

### 4. Webhook Server (`webhook_server.py`)

A complete webhook server implementation:
- Signature verification
- Collection webhook handling
- Payout webhook handling
- Health check endpoint
- Manual verification endpoint

```bash
python webhook_server.py
```

### 5. Flask Integration (`flask_integration.py`)

Full Flask web application integration:
- RESTful API endpoints
- Customer management
- Collection and payout initiation
- Webhook handling
- Web interface
- Error handling

```bash
python flask_integration.py
```

Open your browser to: `http://localhost:5000`

## Example Usage Patterns

### Creating a Customer

```python
from blaaiz import Blaaiz

blaaiz = Blaaiz('your-api-key')

customer = blaaiz.customers.create({
    'first_name': "John",
    'last_name': "Doe",
    'type': "individual",
    'email': "john@example.com",
    'country': "NG",
    'id_type': "passport",
    'id_number': "A12345678"
})
```

### Initiating a Collection

```python
collection = blaaiz.collections.initiate({
    'method': "card",
    'amount': 5000,
    'customer_id': "customer-id",
    'wallet_id': "wallet-id"
})
```

### Processing a Payout

```python
payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "bank_transfer",
    'from_amount': 1000,
    'from_currency_id': "1",
    'to_currency_id': "1",
    'account_number': "0123456789",
    'bank_id': "1"
})
```

### Verifying Webhooks

```python
# In your webhook handler
signature = request.headers.get('x-blaaiz-signature')
payload = request.get_data(as_text=True)

try:
    event = blaaiz.webhooks.construct_event(payload, signature, webhook_secret)
    # Process verified event
except ValueError:
    # Invalid signature
    pass
```

## Testing the Examples

### 1. Test Basic Functionality

```bash
python basic_usage.py
```

Expected output:
```
✓ Connected to Blaaiz API
Found 5 currencies
Found 20 banks
Found 3 wallets
✓ Created customer with ID: cust_abc123
Customer: John Doe
You send: 100000
Recipient gets: 98500
Total fees: 1500
✓ Basic usage example completed successfully!
```

### 2. Test Webhook Server

Start the webhook server:

```bash
python webhook_server.py
```

Test with curl:

```bash
# Test health check
curl http://localhost:5000/health

# Test webhook (replace with actual signature)
curl -X POST http://localhost:5000/webhooks/test \
  -H "Content-Type: application/json" \
  -H "x-blaaiz-signature: sha256=your-signature" \
  -d '{"test": "data"}'
```

### 3. Test Flask Integration

Start the Flask app:

```bash
python flask_integration.py
```

Test API endpoints:

```bash
# Check status
curl http://localhost:5000/api/status

# Create customer
curl -X POST http://localhost:5000/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "type": "individual",
    "email": "john@example.com",
    "country": "NG",
    "id_type": "passport",
    "id_number": "A12345678"
  }'
```

## Common Issues and Solutions

### 1. API Connection Issues

**Problem**: `Failed to connect to Blaaiz API`

**Solutions**:
- Check your API key is correct
- Verify the base URL is correct
- Check your internet connection
- Ensure you're using the correct environment (dev/prod)

### 2. Webhook Signature Verification Fails

**Problem**: `Invalid webhook signature`

**Solutions**:
- Verify your webhook secret is correct
- Ensure you're using the raw request body
- Check that the signature header is being read correctly
- Verify the request is coming from Blaaiz

### 3. File Upload Issues

**Problem**: `File upload failed`

**Solutions**:
- Check file size limits
- Verify file format is supported
- Ensure proper permissions
- Check network connectivity

### 4. Transaction Issues

**Problem**: `Transaction failed` or `Insufficient funds`

**Solutions**:
- Check wallet balance
- Verify customer KYC status
- Ensure all required fields are provided
- Check transaction limits

## Production Considerations

When moving to production:

1. **Environment Variables**: Use proper environment variable management
2. **Error Handling**: Implement comprehensive error handling
3. **Logging**: Add proper logging for debugging
4. **Security**: Implement proper authentication and authorization
5. **Database**: Use a proper database instead of in-memory storage
6. **Rate Limiting**: Implement rate limiting for your API endpoints
7. **Monitoring**: Add monitoring and alerting
8. **Testing**: Write comprehensive tests

## Support

If you encounter any issues with the examples:

1. Check the main README.md for troubleshooting
2. Review the API documentation at https://docs.business.blaaiz.com
3. Contact support at onboarding@blaaiz.com

## Contributing

To add new examples:

1. Create a new Python file in this directory
2. Follow the existing naming convention
3. Add comprehensive comments and error handling
4. Update this README.md with the new example
5. Test thoroughly before submitting