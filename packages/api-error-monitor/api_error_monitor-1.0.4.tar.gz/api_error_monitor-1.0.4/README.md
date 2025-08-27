# api-error-monitor

A Python package for consistent and trackable error monitoring across your API integrations.

## Table of Contents

- [Installation](#installation)
- [Importing](#importing)
- [Adding to requirements.txt](#adding-to-requirementstxt)
- [Overview](#overview)
- [API Error Monitoring](#api-error-monitoring)
- [Best Use Cases for the Monitor Decorator](#best-use-cases-for-the-monitor-decorator)
- [Integration Examples](#integration-examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install api-error-monitor
```

## Importing

After installation, you can import the main classes and decorators in your Python code:

```python
from api_error_monitor import ApiErrorMonitor, monitor_errors
```

## Adding to requirements.txt

To ensure this package is installed automatically in your environment, add the following line to your `requirements.txt` file:

```
pip install api-error-monitor
```

Then install all requirements as usual:

```bash
pip install -r requirements.txt
```

## Overview

When working with external APIs, consistent error monitoring and tracking are essential for:

- Debugging integration issues quickly
- Identifying patterns in API failures
- Improving reliability through better error insights

This package provides tools for tracking, logging, and monitoring API integration errors in a standardized way.

## API Error Monitoring

### Basic Error Monitoring

```python
from api_error_monitor import ApiErrorMonitor
import requests

# Create a monitor for a specific integration
salesforce_monitor = ApiErrorMonitor("salesforce", version="2.0")

try:
    response = requests.get("https://api.salesforce.com/v2/contacts")
    response.raise_for_status()
    # ...use response...
except requests.exceptions.RequestException as e:
    # Capture detailed error information
    salesforce_monitor.capture_http_error(
        exception=e,
        endpoint="/v2/contacts", 
        context={"operation": "list_contacts"}
    )
    raise
```

### Using the Monitor Decorator

```python
from api_error_monitor import monitor_errors

@monitor_errors('stripe', endpoint='create_payment')
def process_stripe_payment(amount, customer_id):
    # Integration code here
    response = stripe.Payment.create(amount=amount, customer=customer_id)
    return response
    # Any errors will be automatically captured with context
```

## Best Use Cases for the Monitor Decorator

The `monitor_errors` decorator is particularly valuable in these scenarios:

1. **API Client Methods**: Decorate methods that communicate with external APIs to automatically track all failures.

   ```python
   class TwitterClient:
       @monitor_errors('twitter', endpoint='get_tweets')
       def get_user_tweets(self, user_id, count=20):
           return self.client.get_user_timeline(user_id=user_id, count=count)
   ```

2. **Scheduled Integration Jobs**: Add monitoring to automated processes that sync with external systems.

   ```python
   @monitor_errors('salesforce', endpoint='daily_sync')
   def run_daily_salesforce_sync():
       fetch_new_records()
       process_records()
       update_local_database()
   ```

3. **Using Context Providers**: Automatically extract relevant parameters for error context.

   ```python
   def payment_context(payment_id, amount, **kwargs):
       return {
           "payment_id": payment_id,
           "amount": amount,
           "currency": kwargs.get('currency', 'USD')
       }
   
   @monitor_errors(
       'payment_processor', 
       endpoint='process_payment',
       context_provider=payment_context
   )
   def process_payment(payment_id, amount, currency='USD'):
       return payment_gateway.charge(payment_id, amount, currency)
   ```

4. **Multiple Integration Points**: Track errors across different systems in complex workflows.

   ```python
   def process_order(order_id):
       inventory = check_inventory(order_id)
       payment = process_payment(order_id)
       shipping = create_shipment(order_id)
       return {"status": "success", "order_id": order_id}
       
   @monitor_errors('inventory_system', endpoint='check')
   def check_inventory(order_id):
       pass
       
   @monitor_errors('payment_gateway', endpoint='charge')
   def process_payment(order_id):
       pass
       
   @monitor_errors('shipping_provider', endpoint='create')
   def create_shipment(order_id):
       pass
   ```

The decorator excels when you need consistent error tracking across many API integration points, want to minimize boilerplate try/except blocks, and need detailed error context for debugging.

### Wrapping API Requests

```python
from api_error_monitor import ApiErrorMonitor
import requests

def get_github_repo_info(repo_name):
    monitor = ApiErrorMonitor("github")
    response = monitor.wrap_request(
        lambda: requests.get(f"https://api.github.com/repos/{repo_name}"),
        endpoint=f"/repos/{repo_name}",
        context={"repo": repo_name},
        request_data={"headers": {"Accept": "application/vnd.github.v3+json"}}
    )
    return response.json()
```

## Integration Examples

```python
from api_error_monitor import ApiErrorMonitor, monitor_errors

class SalesforceIntegration:
    def __init__(self):
        self.client = SalesforceClient()
        self.monitor = ApiErrorMonitor(
            integration_name="salesforce",
            version="2.0",
            context={"org_id": self.client.org_id}
        )
    
    @monitor_errors('salesforce', endpoint='get_contact')
    def get_contact(self, contact_id):
        response = self.monitor.wrap_request(
            lambda: self.client.get(f"/contacts/{contact_id}"),
            endpoint=f"/contacts/{contact_id}",
            context={"contact_id": contact_id}
        )
        return response.json()
```

## API Reference

### `ApiErrorMonitor`

Core monitoring class for API integrations.

Parameters:
- `integration_name` (str): Name of the API integration
- `version` (str, optional): Version of the integration
- `context` (dict, optional): Global context for all errors

Methods:
- `capture_error(message, error_type="GENERAL_ERROR", endpoint=None, status_code=None, request_data=None, response_data=None, exception=None, context=None)`: Record error details with rich context
- `capture_http_error(exception, endpoint, context=None, request_data=None)`: Specialized method for HTTP request exceptions
- `wrap_request(request_func, endpoint, context=None, request_data=None)`: Wrapper for HTTP requests that automatically captures errors
- `get_all_errors()`: Get all errors for the current execution

### `monitor_errors` decorator

Decorator that monitors functions for errors and captures details.

Parameters:
- `integration_name` (str): Name of the API integration
- `endpoint` (str, optional): API endpoint being accessed
- `context_provider` (callable, optional): Function to extract context from arguments

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
