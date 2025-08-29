import os
from browserness import Browserness
from browserness.core.api_error import ApiError

# Initialize the client
# Set your API key as an environment variable named BROWSERNESS_API_KEY
api_key = os.environ.get("BROWSERNESS_API_KEY")
base_url = os.environ.get("BROWSERNESS_BASE_URL")

# Use the built-in token parameter for HTTPBearer authentication
client = Browserness(token=api_key, base_url=base_url)

def main():
    """Demonstrate the complete browser lifecycle workflow."""
    print("=== Browserness SDK Demo: Complete Browser Lifecycle ===")
    print()
    
    try:
        # Step 1: Create a browser
        print("Step 1: Creating a new browser...")
        browser = client.browsers.create_browser(
            headless=True,  # Run in headless mode for the demo
        )
        browser_id = browser.id
        print(f"✓ Browser created successfully!")
        print(f"  Browser ID: {browser_id}")
        print(f"  Status: {browser.status}")
        print(f"  Region: {browser.region}")
        print(f"  Created at: {browser.created_at}")
        if browser.cdp_url:
            print(f"  CDP URL: {browser.cdp_url}")
        if browser.wss_url:
            print(f"  WebSocket URL: {browser.wss_url}")
        print()
        
        # Step 2: Get the browser by ID
        print("Step 2: Retrieving the browser by ID...")
        retrieved_browser = client.browsers.get_browser(browser_id)
        print(f"✓ Browser retrieved successfully!")
        print(f"  Browser ID: {retrieved_browser.id}")
        print(f"  Status: {retrieved_browser.status}")
        print()
        
        # Step 3: List all browsers and check if our browser exists
        print("Step 3: Listing all browsers to verify existence...")
        browsers_list = client.browsers.list_browsers()
        print(f"✓ Found {browsers_list.total} total browsers")
        
        # Check if our browser is in the list
        browser_found = False
        for browser_item in browsers_list.browsers:
            if browser_item.id == browser_id:
                browser_found = True
                print(f"✓ Our browser found in the list:")
                print(f"  ID: {browser_item.id}")
                print(f"  Status: {browser_item.status}")
                break
        
        if not browser_found:
            print(f"✗ Browser {browser_id} not found in the list")
        print()
        
        # Step 4: Delete the browser
        print("Step 4: Deleting the browser...")
        delete_response = client.browsers.delete_browser(browser_id)
        print(f"✓ Browser deleted successfully!")
        print(f"  Response: {delete_response}")
        print()
        
        # Step 5: Try to get the deleted browser (should fail)
        print("Step 5: Attempting to retrieve the deleted browser (should fail)...")
        try:
            deleted_browser = client.browsers.get_browser(browser_id)
            print(f"✗ Unexpected: Browser still exists after deletion!")
            print(f"  Browser: {deleted_browser}")
        except ApiError as api_error:
            print(f"✓ Expected error occurred: Browser not found (Status: {api_error.status_code})")
            print(f"  Error details: {api_error}")
        print()
        
        # Final verification: List browsers again
        print("Final verification: Listing browsers to confirm deletion...")
        final_browsers_list = client.browsers.list_browsers()
        print(f"✓ Current total browsers: {final_browsers_list.total}")
        
        # Verify our browser is no longer in the list
        browser_still_exists = any(b.id == browser_id for b in final_browsers_list.browsers)
        if browser_still_exists:
            print(f"✗ Browser {browser_id} still found in the list after deletion")
        else:
            print(f"✓ Browser {browser_id} successfully removed from the list")
        
        print()
        print("=== Demo completed successfully! ===")
        
    except ApiError as e:
        if e.status_code == 401:
            print("❌ Authentication failed. Please set the BROWSERNESS_API_KEY environment variable.")
            print("   You can get an API key at https://browserness.com")
        else:
            print(f"❌ API Error: {e}")
            print(f"   Status Code: {e.status_code}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
