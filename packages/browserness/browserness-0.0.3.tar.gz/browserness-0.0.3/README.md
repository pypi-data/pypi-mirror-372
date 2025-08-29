# Browserness Python SDK

The official Python SDK for the Browserness API, allowing you to programmatically create and manage remote browser instances.

## Installation

```bash
pip install browserness
```

Or if you're installing from source:

```bash
pip install .
```

## Quick Start

```python
import os
from browserness import Browserness
from browserness.core.api_error import ApiError

# Initialize the client
# Set your API key as an environment variable named BROWSERNESS_API_KEY
api_key = os.environ.get("BROWSERNESS_API_KEY")

# If you have an API key, you can pass it in the headers
headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
client = Browserness(headers=headers)

try:
    # List all browsers (will fail without valid API key)
    browsers = client.browsers.list_browsers()
    print(browsers)
except ApiError as e:
    if e.status_code == 401:
        print("Authentication failed. Please set the BROWSERNESS_API_KEY environment variable.")
        print("You can get an API key at https://browserness.com")
    else:
        print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Async Support

The SDK also includes an async client:

```python
import asyncio
import os
from browserness import AsyncBrowserness
from browserness.core.api_error import ApiError

async def main():
    # Initialize the async client
    # Set your API key as an environment variable named BROWSERNESS_API_KEY
    api_key = os.environ.get("BROWSERNESS_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else None
    client = AsyncBrowserness(headers=headers)
    
    try:
        # List all browsers (will fail without valid API key)
        browsers = await client.browsers.list_browsers()
        print(browsers)
    except ApiError as e:
        if e.status_code == 401:
            print("Authentication failed. Please set the BROWSERNESS_API_KEY environment variable.")
            print("You can get an API key at https://browserness.com")
        else:
            print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(main())
```

## Documentation

For detailed documentation, please refer to the [API documentation](https://api.browserness.com/docs).

## License

This SDK is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.