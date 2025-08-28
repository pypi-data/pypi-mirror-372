# Rhyolite Open Commerce Python SDK

A Python SDK for the Rhyolite Open Commerce API.

## Installation

```bash
pip install rhyolite-open-commerce-sdk
```

## Usage

```python
from rhyolite_open_commerce_sdk import RhyoliteOpenCommerce

# Initialize the client with your credentials
client = RhyoliteOpenCommerce(
    account_id="YOUR_ACCOUNT_ID",
    account_secret="YOUR_ACCOUNT_SECRET"
)

# Get categories
try:
    categories = client.get_categories(page_no=1, page_size=10)
    print(categories)
except Exception as e:
    print(f"An error occurred: {e}")

```
