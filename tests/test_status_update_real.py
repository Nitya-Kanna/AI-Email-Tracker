#!/usr/bin/env python3
"""
End-to-end test for status updates with real email processing

Tests that when an email is processed, the application status updates automatically.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date
from app.database import SessionLocal
from app.models.application import Application, ApplicationStatus
from app.services.email_processor import EmailProcessor


def test_real_status_update():
    """Test status update with real email processing"""
    print("=" * 60)
    print("End-to-End Status Update Test")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Find an existing application to test with
        applications = db.query(Application).all()
        
        if not applications:
            print("❌ No applications found. Please add an application first.")
            return
        
        # Use the first application
        test_app = applications[2]
        print(f"Using application: {test_app.company_name} - {test_app.role_title}")
        print(f"Current status: {test_app.status.value}")
        print(f"Company keyword: {test_app.company_keyword}")
        print()
        
        # Check if there are any emails from this company
        from app.models.email import Email
        existing_emails = db.query(Email).filter(
            Email.application_id == test_app.id
        ).all()
        
        print(f"Found {len(existing_emails)} existing email(s) for this application")
        if existing_emails:
            print("Recent emails:")
            for email in existing_emails[:3]:
                print(f"  - {email.email_type} ({email.classification_confidence:.2f} confidence)")
        print()
        
        # Process emails from this company
        print("Processing new emails from this company...")
        processor = EmailProcessor()
        
        # Get the status before processing
        db.refresh(test_app)
        status_before = test_app.status
        
        # Process emails (this will update status if new emails are found)
        results = processor.process_emails_from_query(
            query=f"from:{test_app.company_keyword}",
            max_results=5
        )
        
        print(f"Processed {results['total_stored']} new email(s)")
        print(f"Matched {results['total_matched']} email(s)")
        print()
        
        # Check status after processing
        db.refresh(test_app)
        status_after = test_app.status
        
        if status_before != status_after:
            print("✓ Status was updated!")
            print(f"  - Before: {status_before.value}")
            print(f"  - After: {status_after.value}")
            
            # Show which email caused the update
            if results['emails']:
                latest_email = results['emails'][0]
                print(f"  - Triggered by: {latest_email['email_type']} email")
        else:
            print("Status unchanged (no status-changing emails found)")
            print(f"  - Current status: {status_after.value}")
        
        print()
        print("=" * 60)
        print("✓ End-to-end test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    test_real_status_update()

