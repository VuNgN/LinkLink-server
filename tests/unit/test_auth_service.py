"""
Unit tests for authentication service
"""

from unittest.mock import AsyncMock

import pytest

from app.core.services.auth_service import AuthService


class TestAuthService:
    """Test authentication service."""

    @pytest.fixture
    def mock_user_repo(self):
        """Mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_token_repo(self):
        """Mock token repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_email_service(self):
        """Mock email service."""
        return AsyncMock()

    @pytest.fixture
    def auth_service(self, mock_user_repo, mock_token_repo, mock_email_service):
        """Create auth service with mocked dependencies."""
        return AuthService(
            mock_user_repo,
            mock_token_repo,
            mock_email_service,
            "test_secret_key",
            "admin@test.com",
        )

    def test_create_access_token(self, auth_service):
        """Test access token creation."""
        username = "testuser"
        token = auth_service._create_access_token(username)
        assert token is not None
        assert len(token) > 20

    def test_create_refresh_token(self, auth_service):
        """Test refresh token creation."""
        username = "testuser"
        token = auth_service._create_refresh_token(username)
        assert token is not None
        assert len(token) > 20

    def test_verify_token_success(self, auth_service):
        """Test successful token verification."""
        username = "testuser"
        token = auth_service._create_access_token(username)
        verified_username = auth_service.verify_token(token)
        assert verified_username == username

    def test_verify_token_invalid(self, auth_service):
        """Test invalid token verification."""
        with pytest.raises(Exception):
            auth_service.verify_token("invalid_token")
