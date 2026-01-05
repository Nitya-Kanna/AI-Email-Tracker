#!/usr/bin/env python3
"""
Test script for GmailService
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.gmail_service import GmailService

def test_gmail_service():
    """Test GmailService functionality"""
    print("=" * 60)
    print("Testing GmailService")
    print("=" * 60)
    print()
    
    try:
        # 1. Create GmailService instance
        print("1. Initializing GmailService...")
        gmail = GmailService()
        print("   ✓ GmailService initialized successfully")
        print()
        
        # 2. Test search queries (try multiple if needed)
        queries = ["from:docker", "from:linkedin", "from:google"]
        emails = None
        
        for query in queries:
            print(f"2. Testing search() with query: '{query}'")
            try:
                emails = gmail.search(query, max_results=5)
                if emails:
                    print(f"   ✓ Found {len(emails)} emails")
                    break
                else:
                    print(f"   ⚠ No emails found for '{query}'")
            except Exception as e:
                print(f"   ✗ Error: {e}")
            
            print()
        
        # 3. Print results
        if emails:
            print("3. Email Results:")
            print("-" * 60)
            print(f"Total emails found: {len(emails)}")
            print()
            
            for i, email in enumerate(emails, 1):
                print(f"Email {i}:")
                print(f"  Sender: {email['sender_email']}")
                print(f"  Subject: {email['subject']}")
                print(f"  Date: {email['date']}")
                snippet_preview = email['snippet'][:100] + "..." if len(email['snippet']) > 100 else email['snippet']
                print(f"  Snippet: {snippet_preview}")
                print()
        else:
            print("3. No emails found with any of the test queries")
            print("   This is normal if you don't have emails from these senders")
        
        print("=" * 60)
        print("Test completed!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("   Make sure credentials.json exists in the project root")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_gmail_service()

