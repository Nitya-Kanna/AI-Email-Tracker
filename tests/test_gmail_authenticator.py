#!/usr/bin/env python3
"""
Test script for GmailAuthenticator

Tests authentication functionality separately from GmailService.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.gmail_authenticator import GmailAuthenticator
from googleapiclient.discovery import build


def test_authenticator():
    """Test GmailAuthenticator functionality"""
    print("=" * 60)
    print("Testing GmailAuthenticator")
    print("=" * 60)
    print()
    
    try:
        # 1. Initialize authenticator
        print("1. Initializing GmailAuthenticator...")
        authenticator = GmailAuthenticator()
        print("   ✓ Authenticator initialized")
        print()
        
        # 2. Get credentials
        print("2. Getting credentials...")
        creds = authenticator.get_credentials()
        print(f"   ✓ Credentials obtained")
        print(f"   - Valid: {creds.valid}")
        print(f"   - Expired: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")
        print()
        
        # 3. Get service
        print("3. Getting Gmail service...")
        service = authenticator.get_service()
        print("   ✓ Service obtained")
        print()
        
        # 4. Test service by getting profile
        print("4. Testing service with profile request...")
        profile = service.users().getProfile(userId='me').execute()
        print(f"   ✓ Profile retrieved")
        print(f"   - Email: {profile.get('emailAddress', 'N/A')}")
        print(f"   - Messages Total: {profile.get('messagesTotal', 'N/A')}")
        print()
        
        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure credentials.json exists in the root directory.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_authenticator()

