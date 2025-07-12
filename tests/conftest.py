"""
Pytest configuration and fixtures for testing
"""

import asyncio
import uuid

import pytest
from httpx import AsyncClient

# Import app without database dependencies
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create test client."""
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def test_user_data():
    """Test user data with unique username."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def approved_test_user_data():
    """Test user data that will be auto-approved for testing."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"approved_{unique_id}",
        "email": f"approved_{unique_id}@example.com",
        "password": "testpass123",
    }


@pytest.fixture
def test_image_data():
    """Test image data."""
    return {
        "filename": "test_image.jpg",
        "original_filename": "test_image.jpg",
        "file_size": 1024,
        "content_type": "image/jpeg",
    }
