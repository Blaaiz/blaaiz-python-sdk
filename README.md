# Blaaiz Python SDK

A comprehensive Python SDK for the Blaaiz RaaS (Remittance as a Service) API. This SDK provides easy-to-use methods for payment processing, collections, payouts, customer management, and more.

## Installation

```bash
pip install blaaiz-python-sdk
```

## Quick Start

```python
from blaaiz import Blaaiz

# Initialize the SDK
blaaiz = Blaaiz('your-api-key-here', base_url='https://api-dev.blaaiz.com')

# Test the connection
is_connected = blaaiz.test_connection()
print(f'API Connected: {is_connected}')
```

## Features

- **Customer Management**: Create, update, and manage customers with KYC verification
- **Collections**: Support for multiple collection methods (Open Banking, Card, Crypto, Bank Transfer)
- **Payouts**: Bank transfers and Interac payouts across multiple currencies
- **Virtual Bank Accounts**: Create and manage virtual accounts for NGN collections
- **Wallets**: Multi-currency wallet management
- **Transactions**: Transaction history and status tracking
- **Webhooks**: Webhook configuration and management with signature verification
- **Files**: Document upload with pre-signed URLs
- **Fees**: Real-time fee calculations and breakdowns
- **Banks & Currencies**: Access to supported banks and currencies

## Supported Currencies & Methods

### Collections
- **CAD**: Interac (push mechanism)
- **NGN**: Bank Transfer (VBA) and Card Payment
- **USD**: Card Payment
- **EUR/GBP**: Open Banking

### Payouts
- **Bank Transfer**: All supported currencies
- **Interac**: CAD transactions

## API Reference

### Customer Management

#### Create a Customer

```python
# Individual customer
customer = blaaiz.customers.create({
    'first_name': "John",  # Required for individual
    'last_name': "Doe",    # Required for individual
    'type': "individual",
    'email': "john.doe@example.com",
    'country': "NG",
    'id_type': "passport",  # drivers_license, passport, id_card, resident_permit
    'id_number': "A12345678",
})

# Business customer
business_customer = blaaiz.customers.create({
    'type': "business",
    'business_name': "Company Name",  # Required for business
    'email': "business@example.com",
    'country': "NG",
    'id_type': "certificate_of_incorporation",
    'id_number': "RC123456",
})

print(f'Customer ID: {customer["data"]["data"]["id"]}')
```

#### Get Customer

```python
customer = blaaiz.customers.get('customer-id')
print(f'Customer: {customer["data"]}')
```

#### List All Customers

```python
customers = blaaiz.customers.list()
print(f'Customers: {customers["data"]}')
```

You can also pass optional filters and opt-in pagination. Supported filters
are `email`, `id_number`, `registration_number`, `verification_status`, and
`type`. Set `paginate=True` to receive a paginated response that includes
`links` and `meta` (with `current_page`, `total`, etc.) alongside `data`.

```python
verified = blaaiz.customers.list({
    "email": "john@example.com",
    "verification_status": "VERIFIED",
    "type": "individual",
    "paginate": True,
})
print(f'Page: {verified["data"]["meta"]["current_page"]}')
print(f'Customers: {verified["data"]["data"]}')
```

#### Update Customer

```python
updated_customer = blaaiz.customers.update('customer-id', {
    'first_name': "Jane",
    'email': "jane.doe@example.com"
})
```

#### List Customer Beneficiaries

```python
beneficiaries = blaaiz.customers.list_beneficiaries('customer-id')
print(f'Beneficiaries: {beneficiaries["data"]}')
```

#### Get Specific Beneficiary

```python
beneficiary = blaaiz.customers.get_beneficiary('customer-id', 'beneficiary-id')
print(f'Beneficiary: {beneficiary["data"]}')

### File Management & KYC

#### Upload Customer Documents

**Method 1: Complete File Upload (Recommended)**
```python
# Option A: Upload from bytes
with open('passport.jpg', 'rb') as f:
    file_data = f.read()

result = blaaiz.customers.upload_file_complete('customer-id', {
    'file': file_data,
    'file_category': 'identity',  # identity, proof_of_address, liveness_check
    'filename': 'passport.jpg',
    'content_type': 'image/jpeg'
})

# Option B: Upload from Base64 string
result = blaaiz.customers.upload_file_complete('customer-id', {
    'file': 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    'file_category': 'identity'
})

# Option C: Upload from Data URL
result = blaaiz.customers.upload_file_complete('customer-id', {
    'file': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    'file_category': 'identity'
})

# Option D: Upload from Public URL
result = blaaiz.customers.upload_file_complete('customer-id', {
    'file': 'https://example.com/documents/passport.jpg',
    'file_category': 'identity'
})

print(f'Upload complete: {result["data"]}')
print(f'File ID: {result["file_id"]}')
```

**Method 2: Manual 3-Step Process**
```python
# Step 1: Get pre-signed URL
presigned_url = blaaiz.files.get_presigned_url({
    'customer_id': 'customer-id',
    'file_category': 'identity'
})

# Step 2: Upload file to the pre-signed URL (implement your file upload logic)
# Step 3: Associate file with customer
file_association = blaaiz.customers.upload_files('customer-id', {
    'id_file': presigned_url['data']['data']['file_id']
})
```

### Collections

#### Initiate Open Banking Collection (EUR/GBP)

```python
collection = blaaiz.collections.initiate({
    'customer_id': "customer-id",
    'wallet_id': "wallet-id",
    'amount': 100.00,
    'currency': "EUR",  # or "GBP"
    'method': "open_banking",
    'phone': "+1234567890"  # Optional
})

print(f'Payment URL: {collection["data"]["url"]}')
print(f'Transaction ID: {collection["data"]["transaction_id"]}')
```

#### Initiate Card Collection (NGN/USD)

```python
collection = blaaiz.collections.initiate({
    'customer_id': "customer-id",
    'wallet_id': "wallet-id",
    'amount': 5000,
    'currency': "NGN",  # or "USD"
    'method': "card",
})

print(f'Payment URL: {collection["data"]["url"]}')
```

#### Crypto Collection

```python
# Get available networks
networks = blaaiz.collections.get_crypto_networks()
print(f'Available networks: {networks["data"]}')

# Initiate crypto collection
crypto_collection = blaaiz.collections.initiate_crypto({
    'amount': 100,
    'network': "ethereum",
    'token': "USDT",
    'wallet_id': "wallet-id"
})
```

#### Attach Customer to Collection

```python
attachment = blaaiz.collections.attach_customer({
    'customer_id': "customer-id",
    'transaction_id': "transaction-id"
})
```

#### Accept Interac Money Request (CAD)

```python
result = blaaiz.collections.accept_interac_money_request({
    'reference_number': "interac-reference-number"
})
```

### Payouts

#### Bank Transfer Payout (NGN)

```python
payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "bank_transfer",
    'from_amount': 1000,  # OR use 'to_amount' for exact recipient amount
    'from_currency_id': "NGN",
    'to_currency_id': "NGN",
    'bank_id': "1",
    'account_number': "0123456789",
})

print(f'Payout Status: {payout["data"]["transaction"]["status"]}')
```

#### Bank Transfer Payout (GBP)

```python
gbp_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "bank_transfer",
    'from_amount': 500,
    'from_currency_id': "GBP",
    'to_currency_id': "GBP",
    'sort_code': "12-34-56",
    'account_number': "12345678",
    'account_name': "John Doe",
})
```

#### Bank Transfer Payout (EUR)

```python
eur_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "bank_transfer",
    'from_amount': 500,
    'from_currency_id': "EUR",
    'to_currency_id': "EUR",
    'iban': "DE89370400440532013000",
    'bic_code': "COBADEFFXXX",
    'account_name': "John Doe",
})
```

#### Interac Payout (CAD)

```python
interac_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "interac",
    'from_amount': 100,
    'from_currency_id': "CAD",
    'to_currency_id': "CAD",
    'email': "recipient@example.com",
    'interac_first_name': "John",
    'interac_last_name': "Doe"
})
```

#### ACH Payout (USD)

```python
ach_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "ach",
    'from_amount': 1000,
    'from_currency_id': "USD",
    'to_currency_id': "USD",
    'type': "individual",  # or "business"
    'account_number': "123456789",
    'account_name': "John Doe",
    'account_type': "checking",  # or "savings"
    'bank_name': "Chase Bank",
    'routing_number': "021000021",
})
```

#### Wire Payout (USD)

```python
wire_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "wire",
    'from_amount': 5000,
    'from_currency_id': "USD",
    'to_currency_id': "USD",
    'type': "individual",
    'account_number': "123456789",
    'account_name': "John Doe",
    'account_type': "checking",
    'bank_name': "Chase Bank",
    'routing_number': "021000021",
    'swift_code': "CHASUS33",
})
```

#### Crypto Payout (USD)

```python
crypto_payout = blaaiz.payouts.initiate({
    'wallet_id': "wallet-id",
    'customer_id': "customer-id",
    'method': "crypto",
    'from_amount': 100,
    'from_currency_id': "USD",
    'to_currency_id': "USD",
    'wallet_address': "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    'wallet_token': "USDT",
    'wallet_network': "ethereum",
})
```

### Virtual Bank Accounts

#### Create Virtual Bank Account

```python
vba = blaaiz.virtual_bank_accounts.create({
    'wallet_id': "wallet-id",
    'account_name': "John Doe"
})

print(f'Account Number: {vba["data"]["account_number"]}')
print(f'Bank Name: {vba["data"]["bank_name"]}')
```

#### List Virtual Bank Accounts

```python
# Filter by wallet ID
vbas = blaaiz.virtual_bank_accounts.list(wallet_id="wallet-id")
print(f'Virtual Accounts: {vbas["data"]}')

# Filter by customer ID
vbas = blaaiz.virtual_bank_accounts.list(customer_id="customer-id")

# Filter by both
vbas = blaaiz.virtual_bank_accounts.list(wallet_id="wallet-id", customer_id="customer-id")
```

#### Get Virtual Bank Account

```python
vba = blaaiz.virtual_bank_accounts.get("vba-id")
print(f'Account Details: {vba["data"]}')
```

#### Close Virtual Bank Account

```python
result = blaaiz.virtual_bank_accounts.close("vba-id", reason="No longer needed")
print(f'Closed: {result["data"]}')
```

#### Get Identification Type Requirements

```python
# Using customer ID
id_types = blaaiz.virtual_bank_accounts.get_identification_type(customer_id="customer-id")

# Using country and type
id_types = blaaiz.virtual_bank_accounts.get_identification_type(country="US", type="individual")
print(f'Required ID Types: {id_types["data"]}')
```

### Wallets

#### List All Wallets

```python
wallets = blaaiz.wallets.list()
print(f'Wallets: {wallets["data"]}')
```

#### Get Specific Wallet

```python
wallet = blaaiz.wallets.get("wallet-id")
print(f'Wallet Balance: {wallet["data"]["balance"]}')
```

### Transactions

#### List Transactions

```python
transactions = blaaiz.transactions.list({
    'page': 1,
    'limit': 10,
    'status': "SUCCESSFUL"  # Optional filter
})

print(f'Transactions: {transactions["data"]}')
```

#### Get Transaction Details

```python
transaction = blaaiz.transactions.get("transaction-id")
print(f'Transaction: {transaction["data"]}')
```

### Banks & Currencies

#### List Banks

```python
banks = blaaiz.banks.list()
print(f'Available Banks: {banks["data"]}')
```

#### Bank Account Lookup

```python
account_info = blaaiz.banks.lookup_account({
    'account_number': "0123456789",
    'bank_id': "1"
})

print(f'Account Name: {account_info["data"]["account_name"]}')
```

#### List Currencies

```python
currencies = blaaiz.currencies.list()
print(f'Supported Currencies: {currencies["data"]}')
```

### Fees

#### Get Fee Breakdown

```python
# Calculate fees based on amount you want to send
fee_breakdown = blaaiz.fees.get_breakdown({
    'from_currency_id': "NGN",
    'to_currency_id': "CAD",
    'from_amount': 100000
})

print(f'You send: {fee_breakdown["data"]["you_send"]}')
print(f'Recipient gets: {fee_breakdown["data"]["recipient_gets"]}')
print(f'Total fees: {fee_breakdown["data"]["total_fees"]}')

# OR calculate fees based on exact amount recipient should receive
fee_breakdown = blaaiz.fees.get_breakdown({
    'from_currency_id': "NGN",
    'to_currency_id': "CAD",
    'to_amount': 500  # Recipient gets exactly 500 CAD
})
```

### Webhooks

#### Register Webhooks

```python
webhook = blaaiz.webhooks.register({
    'collection_url': "https://your-domain.com/webhooks/collection",
    'payout_url': "https://your-domain.com/webhooks/payout"
})
```

#### Get Webhook Configuration

```python
webhook_config = blaaiz.webhooks.get()
print(f'Webhook URLs: {webhook_config["data"]}')
```

#### Replay Webhook

```python
replay = blaaiz.webhooks.replay({
    'transaction_id': "transaction-id"
})
```

#### Simulate Interac Webhook (Non-Production Only)

```python
# Only available in non-production environments
result = blaaiz.webhooks.simulate_interac_webhook({
    'amount': 100,
    'collection_email': "sender@example.com"
})
```

## Advanced Usage

### Complete Payout Workflow

```python
complete_payout_result = blaaiz.create_complete_payout({
    'customer_data': {
        'first_name': "John",
        'last_name': "Doe",
        'type': "individual",
        'email': "john@example.com",
        'country': "NG",
        'id_type': "passport",
        'id_number': "A12345678"
    },
    'payout_data': {
        'wallet_id': "wallet-id",
        'method': "bank_transfer",
        'from_amount': 1000,  # OR 'to_amount' for exact recipient amount
        'from_currency_id': "NGN",
        'to_currency_id': "NGN",
        'bank_id': "1",
        'account_number': "0123456789",
    }
})

print(f'Customer ID: {complete_payout_result["customer_id"]}')
print(f'Payout: {complete_payout_result["payout"]}')
print(f'Fees: {complete_payout_result["fees"]}')
```

### Complete Collection Workflow

```python
complete_collection_result = blaaiz.create_complete_collection({
    'customer_data': {
        'first_name': "Jane",
        'last_name': "Smith",
        'type': "individual",
        'email': "jane@example.com",
        'country': "NG",
        'id_type': "drivers_license",
        'id_number': "ABC123456"
    },
    'collection_data': {
        'method': "card",
        'amount': 5000,
        'currency': "NGN",
        'wallet_id': "wallet-id"
    },
    'create_vba': True  # Optionally create a virtual bank account
})

print(f'Customer ID: {complete_collection_result["customer_id"]}')
print(f'Collection: {complete_collection_result["collection"]}')
print(f'Virtual Account: {complete_collection_result["virtual_account"]}')
```

### Context Manager Support

```python
with Blaaiz('your-api-key') as blaaiz:
    customers = blaaiz.customers.list()
    print(f'Total customers: {len(customers["data"])}')
```

## Error Handling

The SDK uses a custom `BlaaizError` class that provides detailed error information:

```python
from blaaiz import Blaaiz, BlaaizError

try:
    blaaiz = Blaaiz('your-api-key')
    customer = blaaiz.customers.create(invalid_data)
except BlaaizError as e:
    print(f'Blaaiz API Error: {e.message}')
    print(f'Status Code: {e.status}')
    print(f'Error Code: {e.code}')
except Exception as e:
    print(f'Unexpected Error: {str(e)}')
```

## Webhook Handling

### Webhook Signature Verification

The SDK provides built-in webhook signature verification. Blaaiz uses HMAC-SHA256 to sign webhooks with the format `timestamp.payload`.

```python
from blaaiz import Blaaiz

blaaiz = Blaaiz('your-api-key')

# Method 1: Verify signature manually
is_valid = blaaiz.webhooks.verify_signature(
    raw_body,       # Raw webhook payload string
    signature,      # x-blaaiz-signature header
    timestamp,      # x-blaaiz-timestamp header
    webhook_secret  # Your API secret key
)

if is_valid:
    print('Webhook signature is valid')
else:
    print('Invalid webhook signature')

# Method 2: Construct verified event (recommended)
try:
    event = blaaiz.webhooks.construct_event(
        payload,        # Raw webhook payload string
        signature,      # x-blaaiz-signature header
        timestamp,      # x-blaaiz-timestamp header
        webhook_secret  # Your API secret key
    )

    print(f'Verified event: {event}')
    # event['verified'] will be True
    # event['timestamp'] will contain verification timestamp
except ValueError as e:
    print(f'Webhook verification failed: {str(e)}')
```

### Flask Webhook Handler Example

```python
from flask import Flask, request, jsonify
from blaaiz import Blaaiz
import os

app = Flask(__name__)
blaaiz = Blaaiz(os.getenv('BLAAIZ_API_KEY'))

# Webhook secret (your API secret key)
WEBHOOK_SECRET = os.getenv('BLAAIZ_WEBHOOK_SECRET')

@app.route('/webhooks/collection', methods=['POST'])
def handle_collection_webhook():
    signature = request.headers.get('x-blaaiz-signature')
    timestamp = request.headers.get('x-blaaiz-timestamp')
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, timestamp, WEBHOOK_SECRET)

        print(f'Verified collection event: {event}')

        # Process the collection
        # Update your database, send notifications, etc.

        return jsonify({'received': True}), 200

    except ValueError as e:
        print(f'Webhook verification failed: {str(e)}')
        return jsonify({'error': 'Invalid signature'}), 400

@app.route('/webhooks/payout', methods=['POST'])
def handle_payout_webhook():
    signature = request.headers.get('x-blaaiz-signature')
    timestamp = request.headers.get('x-blaaiz-timestamp')
    payload = request.get_data(as_text=True)

    try:
        # Verify webhook signature and construct event
        event = blaaiz.webhooks.construct_event(payload, signature, timestamp, WEBHOOK_SECRET)

        print(f'Verified payout event: {event}')

        # Process the payout completion
        # Update your database, send notifications, etc.

        return jsonify({'received': True}), 200

    except ValueError as e:
        print(f'Webhook verification failed: {str(e)}')
        return jsonify({'error': 'Invalid signature'}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

## Environment Configuration

```python
# Development
blaaiz_dev = Blaaiz('dev-api-key', base_url='https://api-dev.blaaiz.com')

# Production (when available)
blaaiz_prod = Blaaiz('prod-api-key', base_url='https://api.blaaiz.com')
```

## Best Practices

1. **Always validate customer data before creating customers**
2. **Use the fees API to calculate and display fees to users**
3. **Always verify webhook signatures using the SDK's built-in methods**
4. **Store customer IDs and transaction IDs for tracking**
5. **Handle rate limiting gracefully with exponential backoff**
6. **Use environment variables for API keys and webhook secrets**
7. **Implement proper error handling and logging**
8. **Test webhook endpoints thoroughly with signature verification**
9. **Use the context manager for automatic resource cleanup**
10. **Return appropriate HTTP status codes from webhook handlers**

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/blaaiz/blaaiz-python-sdk.git
cd blaaiz-python-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 blaaiz/
black blaaiz/

# Run type checking
mypy blaaiz/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and additional documentation:
- Email: onboarding@blaaiz.com
- Documentation: https://docs.business.blaaiz.com
- Issues: https://github.com/blaaiz/blaaiz-python-sdk/issues

## Changelog

### 1.1.0
- **Customer Service**:
  - Added `list_beneficiaries()` method to list customer beneficiaries
  - Added `get_beneficiary()` method to get specific beneficiary
  - Updated `create()` validation: `first_name`/`last_name` now only required for individuals
- **Collection Service**:
  - Added `accept_interac_money_request()` method for CAD Interac transfers
  - Updated `initiate()` required fields: now requires `customer_id` and `currency`
- **Payout Service**:
  - Added `customer_id` as required field
  - Added support for `to_amount` as alternative to `from_amount`
  - Added currency-specific validation for bank transfers (NGN, GBP, EUR)
  - Added ACH payout support (USD)
  - Added Wire payout support (USD)
  - Added Crypto payout support (USD)
- **Virtual Bank Account Service**:
  - Added `close()` method to close virtual bank accounts
  - Added `get_identification_type()` method for ID type requirements
  - Updated `list()` to support `customer_id` filter parameter
- **Webhook Service**:
  - Added `simulate_interac_webhook()` method (non-production only)
  - Updated `verify_signature()` to use timestamp-based verification
  - Updated `construct_event()` to require timestamp parameter
- **Fees Service**:
  - Added support for `to_amount` as alternative to `from_amount`

### 1.0.0
- Initial release
- Support for all Blaaiz API endpoints
- Comprehensive error handling
- Webhook signature verification
- File upload functionality
- Complete workflow helpers
- Context manager support