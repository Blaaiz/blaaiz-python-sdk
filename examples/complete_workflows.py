"""
Complete Workflows Example for Blaaiz Python SDK
"""

from blaaiz import Blaaiz, BlaaizError

# Initialize the SDK
blaaiz = Blaaiz("your-api-key-here")


def complete_payout_example():
    """Example of a complete payout workflow."""

    print("=== Complete Payout Workflow ===")

    try:
        # Complete payout with customer creation
        result = blaaiz.create_complete_payout(
            {
                "customer_data": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "type": "individual",
                    "email": "john@example.com",
                    "country": "NG",
                    "id_type": "passport",
                    "id_number": "A12345678",
                },
                "payout_data": {
                    "wallet_id": "your-wallet-id",
                    "method": "bank_transfer",
                    "from_amount": 1000,
                    "from_currency_id": "1",  # NGN
                    "to_currency_id": "1",  # NGN
                    "account_number": "0123456789",
                    "bank_id": "1",
                    "phone_number": "+2348012345678",
                },
            }
        )

        print(f"✓ Customer created with ID: {result['customer_id']}")
        print(f"✓ Payout initiated: {result['payout']['message']}")
        print(f"✓ Total fees: {result['fees']['total_fees']}")

    except BlaaizError as e:
        print(f"Payout failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def complete_collection_example():
    """Example of a complete collection workflow."""

    print("\n=== Complete Collection Workflow ===")

    try:
        # Complete collection with customer creation and VBA
        result = blaaiz.create_complete_collection(
            {
                "customer_data": {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "type": "individual",
                    "email": "jane@example.com",
                    "country": "NG",
                    "id_type": "drivers_license",
                    "id_number": "ABC123456",
                },
                "collection_data": {
                    "method": "card",
                    "amount": 5000,
                    "wallet_id": "your-wallet-id",
                },
                "create_vba": True,  # Create virtual bank account
            }
        )

        print(f"✓ Customer created with ID: {result['customer_id']}")
        print(f"✓ Collection initiated: {result['collection']['message']}")

        if result["virtual_account"]:
            print(f"✓ Virtual account created: {result['virtual_account']['account_number']}")

    except BlaaizError as e:
        print(f"Collection failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def interac_payout_example():
    """Example of an Interac payout."""

    print("\n=== Interac Payout Example ===")

    try:
        # Create customer first
        customer = blaaiz.customers.create(
            {
                "first_name": "Bob",
                "last_name": "Johnson",
                "type": "individual",
                "email": "bob@example.com",
                "country": "CA",
                "id_type": "drivers_license",
                "id_number": "D123456789",
            }
        )

        customer_id = customer["data"]["data"]["id"]
        print(f"✓ Customer created: {customer_id}")

        # Initiate Interac payout
        payout = blaaiz.payouts.initiate(
            {
                "wallet_id": "your-wallet-id",
                "customer_id": customer_id,
                "method": "interac",
                "from_amount": 100,
                "from_currency_id": "2",  # CAD
                "to_currency_id": "2",  # CAD
                "email": "recipient@example.com",
                "interac_first_name": "Bob",
                "interac_last_name": "Johnson",
            }
        )

        print(f"✓ Interac payout initiated: {payout['data']['message']}")

    except BlaaizError as e:
        print(f"Interac payout failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def crypto_collection_example():
    """Example of a crypto collection."""

    print("\n=== Crypto Collection Example ===")

    try:
        # Get available networks
        networks = blaaiz.collections.get_crypto_networks()
        print(f"Available networks: {[n['name'] for n in networks['data']]}")

        # Initiate crypto collection
        crypto_collection = blaaiz.collections.initiate_crypto(
            {"amount": 100, "network": "ethereum", "token": "USDT", "wallet_id": "your-wallet-id"}
        )

        print(f"✓ Crypto collection initiated: {crypto_collection['data']['message']}")

    except BlaaizError as e:
        print(f"Crypto collection failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def rates_swaps_refunds_example():
    """Example of the rate, swap and refund services."""

    print("\n=== Rates, Swaps & Refunds Example ===")

    try:
        # List exchange rates (optional search_term filter)
        rates = blaaiz.rates.list({"search_term": "NGN"})
        print(f"Rates: {rates['data']}")

        # Swap funds between two business wallets
        swap = blaaiz.swaps.initiate(
            {
                "from_business_wallet_id": "your-wallet-a",
                "to_business_wallet_id": "your-wallet-b",
                "amount": 100,
                "amount_type": "from",
            }
        )
        print(f"✓ Swap initiated: {swap['data']}")

        # Refund a transaction, then read the refund back
        refund = blaaiz.refunds.initiate(
            {"transaction_id": "your-transaction-id", "reason": "Customer request"}
        )
        refund_id = refund["data"]["id"]
        status = blaaiz.refunds.get(refund_id)
        print(f"✓ Refund {refund_id} status: {status['data']['status']}")

    except BlaaizError as e:
        print(f"Rates/swaps/refunds example failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def merchant_reference_example():
    """Example of attaching a merchant_reference for reconciliation."""

    print("\n=== Merchant Reference Example ===")

    try:
        # merchant_reference is an optional passthrough on payouts and collections;
        # it is unique per business and returned on the resulting transaction.
        payout = blaaiz.payouts.initiate(
            {
                "wallet_id": "your-wallet-id",
                "customer_id": "your-customer-id",
                "method": "bank_transfer",
                "from_amount": 1000,
                "from_currency_id": "1",
                "to_currency_id": "1",
                "bank_id": "1",
                "account_number": "0123456789",
                "merchant_reference": "order-1234",
            }
        )
        print(f"✓ Payout merchant_reference: {payout['data']['transaction']['merchant_reference']}")

        # Look the transaction back up by its merchant_reference
        transaction = blaaiz.transactions.get("order-1234")
        print(f"✓ Resolved transaction: {transaction['data']['id']}")

    except BlaaizError as e:
        print(f"Merchant reference example failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def main():
    """Run all workflow examples."""

    print("Blaaiz Python SDK - Complete Workflows Examples")
    print("=" * 50)

    # Test connection first
    if not blaaiz.test_connection():
        print("✗ Failed to connect to Blaaiz API")
        return

    print("✓ Connected to Blaaiz API\n")

    # Run examples
    complete_payout_example()
    complete_collection_example()
    interac_payout_example()
    crypto_collection_example()
    rates_swaps_refunds_example()
    merchant_reference_example()

    print("\n✓ All workflow examples completed!")


if __name__ == "__main__":
    main()
