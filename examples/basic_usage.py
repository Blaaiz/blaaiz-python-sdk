"""
Basic Usage Example for Blaaiz Python SDK
"""

from blaaiz import Blaaiz, BlaaizError

# Initialize the SDK
blaaiz = Blaaiz('your-api-key-here')

def main():
    """Basic usage examples."""
    
    try:
        # Test connection
        print("Testing connection...")
        if blaaiz.test_connection():
            print("✓ Connected to Blaaiz API")
        else:
            print("✗ Failed to connect to Blaaiz API")
            return
        
        # List currencies
        print("\nFetching supported currencies...")
        currencies = blaaiz.currencies.list()
        print(f"Found {len(currencies['data'])} currencies")
        
        # List banks
        print("\nFetching supported banks...")
        banks = blaaiz.banks.list()
        print(f"Found {len(banks['data'])} banks")
        
        # List wallets
        print("\nFetching wallets...")
        wallets = blaaiz.wallets.list()
        print(f"Found {len(wallets['data'])} wallets")
        
        # Create a customer
        print("\nCreating a customer...")
        customer_data = {
            'first_name': "John",
            'last_name': "Doe",
            'type': "individual",
            'email': "john.doe@example.com",
            'country': "NG",
            'id_type': "passport",
            'id_number': "A12345678"
        }
        
        customer = blaaiz.customers.create(customer_data)
        customer_id = customer['data']['data']['id']
        print(f"✓ Created customer with ID: {customer_id}")
        
        # Get customer details
        print(f"\nFetching customer details...")
        customer_details = blaaiz.customers.get(customer_id)
        print(f"Customer: {customer_details['data']['first_name']} {customer_details['data']['last_name']}")
        
        # Calculate fees
        print("\nCalculating fees...")
        fee_breakdown = blaaiz.fees.get_breakdown({
            'from_currency_id': "1",  # NGN
            'to_currency_id': "2",    # CAD
            'from_amount': 100000
        })
        print(f"You send: {fee_breakdown['data']['you_send']}")
        print(f"Recipient gets: {fee_breakdown['data']['recipient_gets']}")
        print(f"Total fees: {fee_breakdown['data']['total_fees']}")
        
        print("\n✓ Basic usage example completed successfully!")
        
    except BlaaizError as e:
        print(f"Blaaiz API Error: {e.message}")
        print(f"Status Code: {e.status}")
        print(f"Error Code: {e.code}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")

if __name__ == "__main__":
    main()