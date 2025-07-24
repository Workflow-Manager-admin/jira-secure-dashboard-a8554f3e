#!/usr/bin/env python3
"""
Simple test to verify authentication fixes are working.
This script tests the JiraService enhancements.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.jira_service import JiraService
from src.utils.auth import encrypt_api_token, decrypt_api_token, create_access_token
from src.schemas.auth import LoginRequest
from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_jira_service_improvements():
    """Test the improved JiraService error handling."""
    print("=== Testing JiraService Improvements ===")
    
    # Test 1: Invalid domain handling
    print("\n1. Testing invalid domain handling:")
    try:
        jira_service = JiraService(
            jira_domain="invalid-domain-12345.com",
            email="test@example.com",
            api_token="fake-token"
        )
        
        print("   ✓ JiraService created")
        print(f"   - Domain: {jira_service.jira_domain}")
        print(f"   - Base URL: {jira_service.base_url}")
        
        # This should fail with enhanced error message
        try:
            jira_service.validate_credentials()
            print("   ✗ Should have failed with connection error")
            return False
        except HTTPException as e:
            print(f"   ✓ Proper error handling: {e.status_code}")
            print(f"   - Detail: {e.detail}")
            
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False
    
    # Test 2: Domain formatting
    print("\n2. Testing domain formatting:")
    test_domains = [
        "company.atlassian.net",
        "https://company.atlassian.net/",
        "  COMPANY.ATLASSIAN.NET  "
    ]
    
    for domain in test_domains:
        try:
            jira_service = JiraService(
                jira_domain=domain,
                email="test@example.com",
                api_token="test-token"
            )
            print(f"   ✓ '{domain}' -> '{jira_service.jira_domain}'")
        except Exception as e:
            print(f"   ✗ Failed to process '{domain}': {e}")
            return False
    
    return True

def test_input_validation():
    """Test input validation improvements."""
    print("\n=== Testing Input Validation ===")
    
    # Test valid inputs
    try:
        valid_request = LoginRequest(
            email="user@example.com",
            jira_domain="  company.atlassian.net  ",
            api_token="valid-token-123456789"
        )
        print("✓ Valid input processed:")
        print(f"  - Email: {valid_request.email}")
        print(f"  - Domain: {valid_request.jira_domain}")
        print(f"  - Token length: {len(valid_request.api_token)}")
    except Exception as e:
        print(f"✗ Valid input failed: {e}")
        return False
    
    # Test invalid inputs
    invalid_cases = [
        ("invalid-email", "company.atlassian.net", "valid-token", "Invalid email"),
        ("user@example.com", "co", "valid-token", "Domain too short"),
        ("user@example.com", "company.atlassian.net", "short", "Token too short")
    ]
    
    for email, domain, token, description in invalid_cases:
        try:
            LoginRequest(email=email, jira_domain=domain, api_token=token)
            print(f"✗ {description}: Should have failed")
            return False
        except Exception:
            print(f"✓ {description}: Correctly rejected")
    
    return True

def test_token_operations():
    """Test token encryption and JWT operations."""
    print("\n=== Testing Token Operations ===")
    
    try:
        # Test API token encryption
        original_token = "test-api-token-12345"
        encrypted = encrypt_api_token(original_token)
        decrypted = decrypt_api_token(encrypted)
        
        if decrypted == original_token:
            print("✓ API token encryption/decryption working")
        else:
            print("✗ Token encryption failed")
            return False
        
        # Test JWT creation
        test_data = {
            "session_token": "test-session",
            "email": "test@example.com",
            "jira_domain": "test.atlassian.net"
        }
        
        jwt_token = create_access_token(data=test_data)
        if jwt_token and len(jwt_token) > 50:
            print(f"✓ JWT token created: {jwt_token[:30]}...")
        else:
            print("✗ JWT token creation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Token operations failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing Authentication Fixes")
    print("=" * 50)
    
    tests = [
        ("JiraService Improvements", test_jira_service_improvements),
        ("Input Validation", test_input_validation),
        ("Token Operations", test_token_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("The authentication fixes are working correctly.")
    else:
        print(f"\n❌ {total - passed} tests failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
