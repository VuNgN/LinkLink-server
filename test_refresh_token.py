#!/usr/bin/env python3
"""
Test script to verify refresh token functionality
"""


import requests

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def test_refresh_token_flow():
    """Test the complete refresh token flow"""
    print("🧪 Testing Refresh Token Flow")
    print("=" * 50)

    # 1. Login with default admin user
    print("\n1. Logging in with admin user...")
    login_data = {"username": "admin", "password": "admin123"}

    response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=login_data)
    print(f"Login response: {response.status_code}")

    if response.status_code != 200:
        print(f"Login error: {response.text}")
        return False

    login_result = response.json()
    access_token = login_result.get("access_token")
    print(f"Got access token: {access_token[:20]}...")

    # Check cookies
    cookies = response.cookies
    refresh_token_cookie = cookies.get("refresh_token")
    print(f"Refresh token cookie: {'Present' if refresh_token_cookie else 'Missing'}")

    # 2. Test accessing protected endpoint
    print("\n2. Testing protected endpoint...")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}{API_PREFIX}/images", headers=headers)
    print(f"Protected endpoint response: {response.status_code}")

    # 3. Test refresh token
    print("\n3. Testing refresh token...")
    refresh_response = requests.post(
        f"{BASE_URL}{API_PREFIX}/refresh",
        headers={"Content-Type": "application/json"},
        cookies=cookies,
    )

    print(f"Refresh response: {refresh_response.status_code}")
    if refresh_response.status_code == 200:
        refresh_result = refresh_response.json()
        new_access_token = refresh_result.get("access_token")
        print(f"Got new access token: {new_access_token[:20]}...")

        # Test with new token
        headers = {"Authorization": f"Bearer {new_access_token}"}
        response = requests.get(f"{BASE_URL}{API_PREFIX}/images", headers=headers)
        print(f"Protected endpoint with new token: {response.status_code}")

        return True
    else:
        print(f"Refresh error: {refresh_response.text}")
        return False


if __name__ == "__main__":
    try:
        success = test_refresh_token_flow()
        if success:
            print("\n✅ Refresh token test completed successfully!")
        else:
            print("\n❌ Refresh token test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
