# Testing Guide for Blaaiz Python SDK

This guide explains how to run tests for the Blaaiz Python SDK.

## Setup

1. **Install the SDK in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Or install development dependencies manually:**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Running Tests

### Using the Test Runner Script

The easiest way to run tests is using the provided test runner:

```bash
# Run all tests
python run_tests.py

# Run unit tests only
python run_tests.py unit

# Run integration tests only
python run_tests.py integration

# Run tests with coverage
python run_tests.py coverage

# Run linting
python run_tests.py lint

# Run code formatting
python run_tests.py format
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run unit tests only
pytest -m "not integration"

# Run integration tests only
pytest -m integration

# Run with coverage
pytest --cov=blaaiz --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run specific test method
pytest tests/test_client.py::TestBlaaizAPIClient::test_successful_request
```

### Using unittest

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_client

# Run specific test class
python -m unittest tests.test_client.TestBlaaizAPIClient

# Run specific test method
python -m unittest tests.test_client.TestBlaaizAPIClient.test_successful_request
```

### Using Make

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests with coverage
make test-coverage

# Run linting
make lint

# Format code
make format

# Type checking
make type-check
```

## Test Types

### Unit Tests
- **Location**: `tests/test_*.py` (except `test_integration.py`)
- **Purpose**: Test individual components in isolation
- **Requirements**: No external dependencies
- **Run with**: `pytest -m "not integration"`

### Integration Tests
- **Location**: `tests/test_integration.py`
- **Purpose**: Test actual API interactions
- **Requirements**: Valid API key set as `BLAAIZ_API_KEY` environment variable
- **Run with**: `pytest -m integration`

## Environment Variables

For integration tests, set the following environment variables:

```bash
export BLAAIZ_API_KEY="your-api-key"
export BLAAIZ_WEBHOOK_SECRET="your-webhook-secret"
export BLAAIZ_BASE_URL="https://api-dev.blaaiz.com"  # Optional
```

Or create a `.env` file:

```
BLAAIZ_API_KEY=your-api-key
BLAAIZ_WEBHOOK_SECRET=your-webhook-secret
BLAAIZ_BASE_URL=https://api-dev.blaaiz.com
```

## Test Structure

```
tests/
├── __init__.py
├── test_client.py          # HTTP client tests
├── test_error.py           # Error handling tests
├── test_services.py        # Service classes tests
├── test_blaaiz.py          # Main SDK class tests
└── test_integration.py     # Integration tests
```

## Writing Tests

### Unit Test Example

```python
import unittest
from unittest.mock import MagicMock
from blaaiz.services.customer import CustomerService

class TestCustomerService(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.service = CustomerService(self.mock_client)
    
    def test_create_customer(self):
        # Arrange
        customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            # ... other required fields
        }
        self.mock_client.make_request.return_value = {'data': {'id': 'customer-id'}}
        
        # Act
        result = self.service.create(customer_data)
        
        # Assert
        self.mock_client.make_request.assert_called_once_with(
            'POST', '/api/external/customer', customer_data
        )
        self.assertEqual(result['data']['id'], 'customer-id')
```

### Integration Test Example

```python
import unittest
import os
from blaaiz import Blaaiz

class TestBlaaizIntegration(unittest.TestCase):
    def setUp(self):
        api_key = os.getenv('BLAAIZ_API_KEY')
        if not api_key:
            self.skipTest("BLAAIZ_API_KEY not set")
        self.blaaiz = Blaaiz(api_key)
    
    def test_connection(self):
        is_connected = self.blaaiz.test_connection()
        self.assertTrue(is_connected)
```

## Code Quality

### Linting

```bash
# Check code style
flake8 blaaiz/ tests/ examples/

# Format code
black blaaiz/ tests/ examples/

# Type checking
mypy blaaiz/
```

### Coverage

```bash
# Generate coverage report
pytest --cov=blaaiz --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- **Unit tests**: Run on Python 3.7-3.12
- **Integration tests**: Run on main branch pushes
- **Code quality**: Linting, formatting, and type checking
- **Publishing**: Automatic PyPI publishing on releases

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure the SDK is installed in development mode
   ```bash
   pip install -e .
   ```

2. **Integration test failures**: Check that your API key is valid and set correctly
   ```bash
   echo $BLAAIZ_API_KEY
   ```

3. **Coverage not working**: Install coverage package
   ```bash
   pip install coverage pytest-cov
   ```

4. **Linting errors**: Install development dependencies
   ```bash
   pip install -r requirements-dev.txt
   ```

### Performance Tips

- Use `pytest-xdist` for parallel test execution:
  ```bash
  pip install pytest-xdist
  pytest -n auto
  ```

- Skip slow tests during development:
  ```bash
  pytest -m "not slow"
  ```

- Run only failed tests:
  ```bash
  pytest --lf
  ```

## Test Data

### Mock Data

The tests use mock data for unit tests to avoid external dependencies:

```python
# Example mock response
mock_response = {
    'data': {
        'id': 'customer-123',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com'
    }
}
```

### Test Fixtures

For integration tests, you may need:

- Valid API key
- Test wallet ID (set as `BLAAIZ_TEST_WALLET_ID`)
- Test customer data with unique identifiers

## Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow the Arrange-Act-Assert pattern** for clear test structure
3. **Mock external dependencies** in unit tests
4. **Test both success and failure scenarios**
5. **Use proper assertions** with meaningful error messages
6. **Clean up resources** in integration tests
7. **Keep tests isolated** - each test should be independent

## Contributing

When adding new features:

1. **Write tests first** (TDD approach)
2. **Maintain test coverage** above 90%
3. **Update integration tests** for new API endpoints
4. **Add examples** demonstrating new features
5. **Update documentation** for new test scenarios