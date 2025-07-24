"""
Basic tests for authentication functionality.
Tests JWT token creation, validation, and session management.
"""
import pytest
from datetime import timedelta
import os
import sys
from pathlib import Path

# Add project root to Python path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.auth import (
    create_access_token,
    verify_token,
    encrypt_api_token,
    decrypt_api_token,
    generate_session_token
)

class TestAuthUtils:
    """Test authentication utility functions."""
    
    def test_create_and_verify_token(self):
        """Test JWT token creation and verification."""
        # Set up test environment
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
        
        # Test data
        test_data = {
            "email": "test@example.com",
            "jira_domain": "test.atlassian.net",
            "session_token": "test-session-token"
        }
        
        # Create token
        token = create_access_token(data=test_data)
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        payload = verify_token(token)
        assert payload["email"] == test_data["email"]
        assert payload["jira_domain"] == test_data["jira_domain"]
        assert payload["session_token"] == test_data["session_token"]
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Test token expiration handling."""
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
        
        # Create expired token
        test_data = {"email": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        
        token = create_access_token(data=test_data, expires_delta=expires_delta)
        
        # Verify that expired token raises exception
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token(token)
    
    def test_encrypt_decrypt_api_token(self):
        """Test API token encryption and decryption."""
        # Set up test environment
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        os.environ["ENCRYPTION_KEY"] = test_key
        
        # Test API token
        original_token = "test-api-token-12345"
        
        # Encrypt token
        encrypted_token = encrypt_api_token(original_token)
        assert isinstance(encrypted_token, str)
        assert encrypted_token != original_token
        
        # Decrypt token
        decrypted_token = decrypt_api_token(encrypted_token)
        assert decrypted_token == original_token
    
    def test_generate_session_token(self):
        """Test session token generation."""
        token1 = generate_session_token()
        token2 = generate_session_token()
        
        assert isinstance(token1, str)
        assert isinstance(token2, str)
        assert len(token1) > 0
        assert len(token2) > 0
        assert token1 != token2  # Should be unique

if __name__ == "__main__":
    # Run basic tests
    test_class = TestAuthUtils()
    
    print("Running basic authentication tests...")
    
    try:
        test_class.test_create_and_verify_token()
        print("✓ Token creation/verification test passed")
    except Exception as e:
        print(f"✗ Token test failed: {e}")
    
    try:
        test_class.test_encrypt_decrypt_api_token()
        print("✓ API token encryption test passed")
    except Exception as e:
        print(f"✗ Encryption test failed: {e}")
    
    try:
        test_class.test_generate_session_token()
        print("✓ Session token generation test passed")
    except Exception as e:
        print(f"✗ Session token test failed: {e}")
    
    print("\nBasic tests completed.")
