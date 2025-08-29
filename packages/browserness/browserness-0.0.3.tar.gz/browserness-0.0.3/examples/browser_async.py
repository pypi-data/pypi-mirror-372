import asyncio
import os
from browserness import AsyncBrowserness
from browserness.core.api_error import ApiError

async def main():
    # Initialize the async client
    # Set your API key as an environment variable named BROWSERNESS_API_KEY
    api_key = os.environ.get("BROWSERNESS_API_KEY")
    
    # Use the built-in token parameter for HTTPBearer authentication
    client = AsyncBrowserness(token=api_key, base_url="http://localhost:8000")
    
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

if __name__ == "__main__":
    asyncio.run(main())