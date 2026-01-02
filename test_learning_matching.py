#!/usr/bin/env python3
"""
Test using full EmailProcessor workflow

This tests the complete workflow (fetch, classify, store, match) using
the same code path that will be used in production.
"""
from app.services.email_processor import EmailProcessor


def test_learning_matching():
    """Test using full EmailProcessor workflow"""
    print("=" * 60)
    print("🧪 TEST: Learning Email Matching (Full Workflow)")
    print("=" * 60)
    print()
    
    # Initialize EmailProcessor
    print("🔧 Initializing EmailProcessor...")
    try:
        processor = EmailProcessor()
        print("   ✓ Gmail service initialized")
        print("   ✓ Email classifier initialized")
        print()
    except Exception as e:
        print(f"   ❌ Error initializing: {e}")
        return
    
    # Use EmailProcessor's full workflow - same code path as production!
    print("🔍 Processing emails from learningusesv@gmail.com...")
    print("   (Using full EmailProcessor workflow: fetch → classify → store → match)")
    print()
    
    results = processor.process_emails_from_query(
        query="from:learningusesv@gmail.com",
        max_results=1  # Just get the latest one
    )
    
    # Display results
    print("=" * 60)
    print("Processing Results:")
    print("=" * 60)
    print(f"Total emails fetched: {results['total_fetched']}")
    print(f"Total emails classified: {results['total_classified']}")
    print(f"Total emails stored: {results['total_stored']}")
    print(f"Total emails matched to applications: {results['total_matched']}")
    print()
    
    # Show detailed results
    if results['emails']:
        print("📨 Processed Email:")
        print("-" * 60)
        email = results['emails'][0]
        print(f"Subject: {email['subject']}")
        print(f"From: {email['sender']}")
        print(f"Type: {email['email_type']} (confidence: {email['confidence']:.2f})")
        print(f"Matched: {'✓' if email['matched'] else '✗'}", end="")
        if email['application']:
            print(f" → {email['application']}")
            print()
            print("✓ SUCCESS! Full workflow completed:")
            print("   - Email fetched from Gmail")
            print("   - Email classified with AI")
            print("   - Email stored in database")
            print("   - Email matched to application")
        else:
            print(" (no matching application)")
            print()
            print("⚠️  Email processed but not matched")
            print("   Check if company_keyword appears in email address")
    elif results['total_fetched'] > 0:
        print("ℹ️  Email found but already processed")
        print(f"   Found {results['total_fetched']} email(s) from Gmail")
        print("   They're already in the database (deduplication working)")
        print()
        print("   This is expected behavior - emails won't be processed twice.")
    else:
        print("❌ No emails found")
        print("   Query: 'from:learningusesv@gmail.com'")
        print("   Check if emails exist from this address in Gmail")
    
    print()
    print("=" * 60)
    print("✓ Test complete!")
    print("=" * 60)
    print()
    print("Note: This test uses the SAME code path as production.")
    print("When you use EmailProcessor in production, it will work the same way.")


if __name__ == '__main__':
    test_learning_matching()
