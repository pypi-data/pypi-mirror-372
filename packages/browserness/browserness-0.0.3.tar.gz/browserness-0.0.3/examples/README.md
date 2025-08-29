# Browserness Python SDK Examples

This directory contains example scripts demonstrating how to use the Browserness Python SDK.

## Examples

1. `browser_basic.py` - Comprehensive browser lifecycle demonstration including:
   - Creating a browser instance
   - Retrieving browser details by ID
   - Listing all browsers and verifying existence
   - Deleting the browser
   - Attempting to retrieve the deleted browser (error handling)
   - Final verification of deletion

2. `browser_async.py` - Async usage of the SDK

## Usage

Before running the examples, set your Browserness API key as an environment variable:

```bash
export BROWSERNESS_API_KEY=your_api_key_here
```

Then run the examples:

```bash
# Basic example
python browser_basic.py

# Async example
python browser_async.py
```

## Authentication

The examples show how to authenticate with the Browserness API using the built-in token parameter:

```python
api_key = os.environ.get("BROWSERNESS_API_KEY")
client = Browserness(token=api_key, base_url="http://localhost:8000")
```

If you don't have an API key yet, you can get one at [https://browserness.com](https://browserness.com).