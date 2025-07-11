#!/usr/bin/env python3
"""
Test client for the Clean Architecture Image Upload Server
This script demonstrates how to use all the API endpoints
"""

import json
import os

import requests

# Server configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"


def print_response(response, title=""):
    """Pretty print API response"""
    print(f"\n{'='*50}")
    if title:
        print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print(f"{'='*50}")


def test_authentication():
    """Test authentication endpoints"""
    print("🔐 Testing Authentication...")

    # Test registration
    print("\n1. Testing user registration...")
    register_data = {"username": "testuser", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}{API_PREFIX}/register", json=register_data)
    print_response(response, "User Registration")

    # Test login
    print("\n2. Testing login...")
    login_data = {"username": "admin", "password": "admin123"}  # Use default admin user
    response = requests.post(f"{BASE_URL}{API_PREFIX}/login", json=login_data)
    print_response(response, "User Login")

    if response.status_code == 200:
        tokens = response.json()
        return tokens
    else:
        print("❌ Login failed!")
        return None


def test_image_upload(tokens):
    """Test image upload functionality"""
    print("\n📸 Testing Image Upload...")

    if not tokens:
        print("❌ No tokens available for upload test")
        return

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Create a test image if it doesn't exist
    test_image_path = "test_image.jpg"
    if not os.path.exists(test_image_path):
        print(f"Creating test image: {test_image_path}")
        # Create a simple test image using PIL
        try:
            from PIL import Image, ImageDraw

            img = Image.new("RGB", (200, 200), color="red")
            draw = ImageDraw.Draw(img)
            draw.text((50, 90), "Test Image", fill="white")
            img.save(test_image_path)
        except ImportError:
            print("PIL not available, skipping image creation")
            return

    # Upload image
    print(f"\n3. Uploading image: {test_image_path}")
    with open(test_image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/upload-image", headers=headers, files=files
        )
        print_response(response, "Image Upload")

    return response.json().get("filename") if response.status_code == 200 else None


def test_image_management(tokens, uploaded_filename=None):
    """Test image management endpoints"""
    print("\n📋 Testing Image Management...")

    if not tokens:
        print("❌ No tokens available for management test")
        return

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Get all images
    print("\n4. Getting all images...")
    response = requests.get(f"{BASE_URL}{API_PREFIX}/images", headers=headers)
    print_response(response, "Get All Images")

    if response.status_code == 200:
        images = response.json()
        if images and uploaded_filename:
            # Get specific image info
            print(f"\n5. Getting specific image: {uploaded_filename}")
            response = requests.get(
                f"{BASE_URL}{API_PREFIX}/image/{uploaded_filename}", headers=headers
            )
            print_response(response, "Get Specific Image")


def test_token_refresh(tokens):
    """Test token refresh functionality"""
    print("\n🔄 Testing Token Refresh...")

    if not tokens or "refresh_token" not in tokens:
        print("❌ No refresh token available")
        return

    # Refresh token
    print("\n6. Refreshing access token...")
    refresh_data = {"refresh_token": tokens["refresh_token"]}
    response = requests.post(f"{BASE_URL}{API_PREFIX}/refresh", json=refresh_data)
    print_response(response, "Token Refresh")

    if response.status_code == 200:
        new_tokens = response.json()
        return new_tokens
    return None


def test_logout(tokens):
    """Test logout functionality"""
    print("\n🚪 Testing Logout...")

    if not tokens:
        print("❌ No tokens available for logout test")
        return

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    logout_data = {"refresh_token": tokens["refresh_token"]}

    print("\n7. Logging out...")
    response = requests.post(
        f"{BASE_URL}{API_PREFIX}/logout", headers=headers, json=logout_data
    )
    print_response(response, "Logout")


def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")


def main():
    """Run all tests"""
    print("🚀 Starting Clean Architecture Image Upload Server Tests")
    print(f"Server URL: {BASE_URL}")
    print(f"API Prefix: {API_PREFIX}")

    try:
        # Test health check
        test_health_check()

        # Test authentication
        tokens = test_authentication()

        if tokens:
            # Test image upload
            uploaded_filename = test_image_upload(tokens)

            # Test image management
            test_image_management(tokens, uploaded_filename)

            # Test token refresh
            new_tokens = test_token_refresh(tokens)

            # Test logout
            test_logout(tokens if new_tokens is None else new_tokens)

        print("\n✅ All tests completed!")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to server at {BASE_URL}")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")


if __name__ == "__main__":
    main()
