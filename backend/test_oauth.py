#!/usr/bin/env python3
"""Quick test script for OAuth endpoints."""

import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_oauth_endpoints():
    """Test OAuth endpoints."""
    print("=" * 60)
    print("Testing OAuth Endpoints")
    print("=" * 60)
    
    providers = ["google", "github", "facebook", "apple"]
    redirect_uri = "http://localhost:3000/callback"
    
    for provider in providers:
        print(f"\n[Testing {provider.upper()} OAuth]")
        print("-" * 60)
        
        # Test authorize endpoint
        url = f"{BASE_URL}/api/v1/auth/oauth/{provider}/authorize"
        params = {"redirect_uri": redirect_uri}
        
        try:
            response = requests.get(url, params=params, timeout=5)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Authorize URL generated")
                print(f"   State: {data.get('state', 'N/A')}")
                
                # Parse the authorize URL to show it's valid
                auth_url = data.get('authorize_url', '')
                if auth_url:
                    parsed = urlparse(auth_url)
                    print(f"   Provider URL: {parsed.scheme}://{parsed.netloc}{parsed.path}")
                    query_params = parse_qs(parsed.query)
                    print(f"   Has client_id: {'client_id' in query_params}")
                    print(f"   Has state: {'state' in query_params}")
                    print(f"   Has redirect_uri: {'redirect_uri' in query_params}")
            elif response.status_code == 500:
                error_data = response.json()
                print(f"❌ Error: {error_data.get('detail', 'Unknown error')}")
                if "not configured" in error_data.get('detail', '').lower():
                    print(f"   ℹ️  {provider.upper()} OAuth credentials not configured")
                    print(f"   ℹ️  Add OAUTH_{provider.upper()}_CLIENT_ID and OAUTH_{provider.upper()}_CLIENT_SECRET to .env")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Server not running")
            print(f"   Start server with: uvicorn app.main:app --reload")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("\nTo test OAuth endpoints:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Configure OAuth credentials in .env file")
    print("3. Restart the server")
    print("4. Run this script again: python3 test_oauth.py")
    print("\nFor full OAuth flow testing:")
    print("1. Set up OAuth app with provider (see OAUTH_SETUP.md)")
    print("2. Add credentials to .env file")
    print("3. Test authorize endpoint - open the authorize_url in browser")
    print("4. Complete OAuth flow and verify callback")

if __name__ == "__main__":
    test_oauth_endpoints()

