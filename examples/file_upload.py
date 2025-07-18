"""
File Upload Example for Blaaiz Python SDK

This example demonstrates various ways to upload files for KYC verification.
"""

from blaaiz import Blaaiz, BlaaizError
import base64
import os

# Initialize the SDK
blaaiz = Blaaiz('your-api-key-here')

def create_sample_customer():
    """Create a sample customer for file upload examples."""
    
    customer_data = {
        'first_name': "John",
        'last_name': "Doe",
        'type': "individual",
        'email': "john.doe@example.com",
        'country': "NG",
        'id_type': "passport",
        'id_number': "A12345678"
    }
    
    try:
        customer = blaaiz.customers.create(customer_data)
        customer_id = customer['data']['data']['id']
        print(f"✓ Created customer with ID: {customer_id}")
        return customer_id
    except BlaaizError as e:
        print(f"Failed to create customer: {e.message}")
        return None

def upload_from_file_example(customer_id):
    """Example: Upload file from local file system."""
    
    print("\n=== Upload from File Example ===")
    
    try:
        # Create a sample file for demonstration
        sample_file_path = "/tmp/sample_passport.txt"
        with open(sample_file_path, 'w') as f:
            f.write("This is a sample passport document for testing")
        
        # Read file and upload
        with open(sample_file_path, 'rb') as f:
            file_data = f.read()
        
        result = blaaiz.customers.upload_file_complete(customer_id, {
            'file': file_data,
            'file_category': 'identity',
            'filename': 'passport.txt',
            'content_type': 'text/plain'
        })
        
        print(f"✓ File uploaded successfully")
        print(f"  File ID: {result['file_id']}")
        print(f"  Upload URL: {result['presigned_url']}")
        
        # Clean up
        os.remove(sample_file_path)
        
    except BlaaizError as e:
        print(f"File upload failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def upload_from_base64_example(customer_id):
    """Example: Upload file from base64 string."""
    
    print("\n=== Upload from Base64 Example ===")
    
    try:
        # Sample base64 encoded image (1x1 pixel PNG)
        base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        result = blaaiz.customers.upload_file_complete(customer_id, {
            'file': base64_data,
            'file_category': 'proof_of_address',
            'filename': 'address_proof.png',
            'content_type': 'image/png'
        })
        
        print(f"✓ Base64 file uploaded successfully")
        print(f"  File ID: {result['file_id']}")
        
    except BlaaizError as e:
        print(f"Base64 upload failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def upload_from_data_url_example(customer_id):
    """Example: Upload file from data URL."""
    
    print("\n=== Upload from Data URL Example ===")
    
    try:
        # Sample data URL (1x1 pixel PNG)
        data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        result = blaaiz.customers.upload_file_complete(customer_id, {
            'file': data_url,
            'file_category': 'liveness_check',
            'filename': 'liveness_check.png'  # Optional - will be auto-detected
        })
        
        print(f"✓ Data URL file uploaded successfully")
        print(f"  File ID: {result['file_id']}")
        
    except BlaaizError as e:
        print(f"Data URL upload failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def upload_from_url_example(customer_id):
    """Example: Upload file from public URL."""
    
    print("\n=== Upload from URL Example ===")
    
    try:
        # Sample public URL (placeholder image)
        public_url = "https://via.placeholder.com/150x150.png"
        
        result = blaaiz.customers.upload_file_complete(customer_id, {
            'file': public_url,
            'file_category': 'identity'
            # filename and content_type will be auto-detected
        })
        
        print(f"✓ URL file uploaded successfully")
        print(f"  File ID: {result['file_id']}")
        
    except BlaaizError as e:
        print(f"URL upload failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def manual_upload_example(customer_id):
    """Example: Manual 3-step upload process."""
    
    print("\n=== Manual Upload Process Example ===")
    
    try:
        # Step 1: Get presigned URL
        print("Step 1: Getting presigned URL...")
        presigned_response = blaaiz.files.get_presigned_url({
            'customer_id': customer_id,
            'file_category': 'identity'
        })
        
        file_id = presigned_response['data']['data']['file_id']
        print(f"✓ Got presigned URL and file ID: {file_id}")
        
        # Step 2: Upload file (normally you would upload to the presigned URL)
        print("Step 2: Uploading file to S3 (skipped in example)")
        
        # Step 3: Associate file with customer
        print("Step 3: Associating file with customer...")
        file_association = blaaiz.customers.upload_files(customer_id, {
            'id_file': file_id
        })
        
        print(f"✓ File associated with customer successfully")
        
    except BlaaizError as e:
        print(f"Manual upload failed: {e.message}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

def batch_upload_example(customer_id):
    """Example: Upload multiple files for a customer."""
    
    print("\n=== Batch Upload Example ===")
    
    files_to_upload = [
        {
            'file': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            'file_category': 'identity',
            'filename': 'passport.png'
        },
        {
            'file': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            'file_category': 'proof_of_address',
            'filename': 'utility_bill.png'
        },
        {
            'file': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            'file_category': 'liveness_check',
            'filename': 'selfie.png'
        }
    ]
    
    uploaded_files = []
    
    for i, file_info in enumerate(files_to_upload, 1):
        try:
            print(f"Uploading file {i}/{len(files_to_upload)}: {file_info['filename']}")
            
            result = blaaiz.customers.upload_file_complete(customer_id, file_info)
            uploaded_files.append(result)
            
            print(f"✓ {file_info['filename']} uploaded successfully")
            
        except BlaaizError as e:
            print(f"✗ Failed to upload {file_info['filename']}: {e.message}")
        except Exception as e:
            print(f"✗ Unexpected error uploading {file_info['filename']}: {str(e)}")
    
    print(f"\n✓ Batch upload completed: {len(uploaded_files)}/{len(files_to_upload)} files uploaded")

def main():
    """Run all file upload examples."""
    
    print("Blaaiz Python SDK - File Upload Examples")
    print("=" * 50)
    
    # Test connection
    if not blaaiz.test_connection():
        print("✗ Failed to connect to Blaaiz API")
        return
    
    print("✓ Connected to Blaaiz API")
    
    # Create a customer for file uploads
    customer_id = create_sample_customer()
    if not customer_id:
        print("✗ Failed to create customer - cannot proceed with file uploads")
        return
    
    # Run file upload examples
    upload_from_file_example(customer_id)
    upload_from_base64_example(customer_id)
    upload_from_data_url_example(customer_id)
    upload_from_url_example(customer_id)
    manual_upload_example(customer_id)
    batch_upload_example(customer_id)
    
    print("\n✓ All file upload examples completed!")

if __name__ == "__main__":
    main()