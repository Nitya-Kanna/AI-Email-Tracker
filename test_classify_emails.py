#!/usr/bin/env python3
"""
Test script to manually classify and process emails

This script:
1. Fetches emails from companies you've applied to
2. Classifies them using Gemini AI
3. Stores them in the database
4. Matches them to applications
"""
from app.services.email_processor import EmailProcessor
from app.database import SessionLocal
from app.models.application import Application

def main():
    """Main function to process emails"""
    print("=" * 60)
    print("Email Classification and Processing")
    print("=" * 60)
    print()
    
    # Get company keywords from your applications
    db = SessionLocal()
    try:
        applications = db.query(Application).all()
        company_keywords = [app.company_keyword for app in applications]
        
        if not company_keywords:
            print("❌ No applications found. Please add applications first.")
            return
        
        print(f"📋 Found {len(applications)} application(s):")
        for app in applications:
            print(f"   - {app.company_name} ({app.company_keyword})")
        print()
        
    finally:
        db.close()
    
    # Initialize processor
    print("🔧 Initializing email processor...")
    try:
        processor = EmailProcessor()
        print("   ✓ Gmail service initialized")
        print("   ✓ Email classifier initialized")
        print()
    except Exception as e:
        print(f"   ❌ Error initializing: {e}")
        return
    
    # Process emails from companies
    print(f"📧 Processing emails from companies: {', '.join(company_keywords)}")
    print()
    
    try:
        results = processor.process_emails_from_companies(
            company_keywords=company_keywords,
            max_results=50
        )
        
        # Display results
        print("=" * 60)
        print("Processing Results")
        print("=" * 60)
        print(f"Total emails fetched: {results['total_fetched']}")
        print(f"Total emails classified: {results['total_classified']}")
        print(f"Total emails stored: {results['total_stored']}")
        print(f"Total emails matched to applications: {results['total_matched']}")
        print()
        
        if results['emails']:
            print("📨 Processed Emails:")
            print("-" * 60)
            for i, email in enumerate(results['emails'], 1):
                print(f"\n{i}. {email['subject']}")
                print(f"   From: {email['sender']}")
                print(f"   Type: {email['email_type']} (confidence: {email['confidence']:.2f})")
                print(f"   Matched: {'✓' if email['matched'] else '✗'}", end="")
                if email['application']:
                    print(f" → {email['application']}")
                else:
                    print(" (no matching application)")
        else:
            print("No new emails to process.")
        
        print()
        print("=" * 60)
        print("✓ Processing complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error processing emails: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

