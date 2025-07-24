#!/usr/bin/env python3
"""
Real Jira authentication testing tool.
This script allows testing with actual Jira credentials to verify fixes.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.jira_service import JiraService
from src.schemas.auth import LoginRequest
from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_jira_credentials():
    """Test with real Jira credentials provided by user."""
    print("🔐 Real Jira Authentication Test")
    print("=" * 50)
    print("This tool tests authentication with your actual Jira credentials.")
    print("Your credentials are not stored and are only used for testing.\n")
    
    # Get credentials
    email = input("Enter your Jira email: ").strip()
    domain = input("Enter your Jira domain (e.g., company.atlassian.net): ").strip()
    api_token = input("Enter your Jira API token: ").strip()
    
    if not all([email, domain, api_token]):
        print("❌ All fields are required!")
        return False
    
    print("\n📋 Testing with:")
    print(f"Email: {email}")
    print(f"Domain: {domain}")
    print(f"API Token: {'*' * min(len(api_token), 10)}...")
    
    # Test input validation
    print("\n🔍 Step 1: Input Validation")
    try:
        login_request = LoginRequest(
            email=email,
            jira_domain=domain,
            api_token=api_token
        )
        print("✓ Input validation passed")
        print(f"  - Cleaned domain: {login_request.jira_domain}")
    except Exception as e:
        print(f"✗ Input validation failed: {e}")
        return False
    
    # Test JiraService creation
    print("\n🔍 Step 2: JiraService Creation")
    try:
        jira_service = JiraService(
            jira_domain=login_request.jira_domain,
            email=login_request.email,
            api_token=login_request.api_token
        )
        print("✓ JiraService created successfully")
        print(f"  - Domain: {jira_service.jira_domain}")
        print(f"  - Base URL: {jira_service.base_url}")
    except Exception as e:
        print(f"✗ JiraService creation failed: {e}")
        return False
    
    # Test credential validation
    print("\n🔍 Step 3: Credential Validation")
    try:
        result = jira_service.validate_credentials()
        if result:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed (returned False)")
            return False
    except HTTPException as e:
        print(f"❌ Authentication failed: {e.detail}")
        print(f"   Status Code: {e.status_code}")
        
        # Provide helpful suggestions based on error
        if e.status_code == 401:
            print("\n💡 Troubleshooting suggestions:")
            print("   1. Verify your API token is correct and not expired")
            print("   2. Check that your email address is correct")
            print("   3. Ensure your Jira account has API access enabled")
        elif e.status_code == 403:
            print("\n💡 Troubleshooting suggestions:")
            print("   1. Check that your account has appropriate Jira permissions")
            print("   2. Verify your account is not disabled")
        elif e.status_code == 502 or e.status_code == 404:
            print("\n💡 Troubleshooting suggestions:")
            print("   1. Verify your domain format (e.g., company.atlassian.net)")
            print("   2. Check that your Jira instance is accessible")
            print("   3. Try accessing your Jira instance in a web browser")
        
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test project retrieval
    print("\n🔍 Step 4: Project Retrieval")
    try:
        projects = jira_service.get_user_projects()
        print(f"✅ Successfully retrieved {len(projects)} projects")
        
        if projects:
            print("\n📋 Sample projects:")
            for i, project in enumerate(projects[:3]):  # Show first 3
                print(f"   {i+1}. {project['name']} ({project['key']})")
                if project.get('lead', {}).get('name'):
                    print(f"      Lead: {project['lead']['name']}")
        else:
            print("   No projects found (this might be normal if you don't have project access)")
            
    except HTTPException as e:
        print(f"❌ Project retrieval failed: {e.detail}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during project retrieval: {e}")
        return False
    
    return True

def main():
    """Main function."""
    try:
        print("This tool helps diagnose Jira authentication issues.")
        print("It will test the complete authentication flow with your credentials.\n")
        
        proceed = input("Do you want to proceed? (y/N): ").strip().lower()
        if proceed != 'y':
            print("Test cancelled.")
            return
        
        success = test_real_jira_credentials()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 All tests passed! Your Jira authentication is working correctly.")
            print("The backend should now be able to authenticate users successfully.")
        else:
            print("❌ Authentication test failed.")
            print("Please check the errors above and verify your credentials.")
            print("\nCommon issues and solutions:")
            print("1. API Token: Generate a new one at https://id.atlassian.com/manage-profile/security/api-tokens")
            print("2. Domain: Use format like 'company.atlassian.net' (no https://)")
            print("3. Email: Use the email associated with your Jira account")
            print("4. Permissions: Ensure your account has API access")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logger.exception("Detailed error:")

if __name__ == "__main__":
    main()
