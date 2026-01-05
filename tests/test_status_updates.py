#!/usr/bin/env python3
"""
Test script for application status updates

Tests that application status automatically updates when emails are processed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date, datetime
from app.database import SessionLocal
from app.models.application import Application, ApplicationStatus
from app.models.email import Email
from app.services.email_processor import EmailProcessor


def test_status_updates():
    """Test that application status updates correctly based on email type"""
    print("=" * 60)
    print("Testing Application Status Updates")
    print("=" * 60)
    print()
    
    db = SessionLocal()
    try:
        # Clean up any existing test applications
        test_apps = db.query(Application).filter(
            Application.company_keyword == "teststatus"
        ).all()
        for app in test_apps:
            db.delete(app)
        db.commit()
        
        # Create a test application
        print("1. Creating test application...")
        test_app = Application(
            company_name="Test Status Company",
            company_keyword="teststatus",
            role_title="Software Engineer",
            applied_date=date.today(),
            status=ApplicationStatus.APPLIED
        )
        db.add(test_app)
        db.commit()
        db.refresh(test_app)
        
        print(f"   ✓ Created application: {test_app.company_name}")
        print(f"   - Initial status: {test_app.status.value}")
        print()
        
        # Test different email types and status transitions
        test_cases = [
            {
                "email_type": "acknowledgment",
                "expected_status": ApplicationStatus.SCREENING,
                "description": "Acknowledgment should move from APPLIED to SCREENING"
            },
            {
                "email_type": "interview_request",
                "expected_status": ApplicationStatus.INTERVIEW,
                "description": "Interview request should move from SCREENING to INTERVIEW"
            },
            {
                "email_type": "offer",
                "expected_status": ApplicationStatus.OFFER,
                "description": "Offer should move from INTERVIEW to OFFER"
            },
            {
                "email_type": "rejection",
                "expected_status": ApplicationStatus.REJECTED,
                "description": "Rejection should move to REJECTED"
            },
        ]
        
        processor = EmailProcessor()
        
        for i, test_case in enumerate(test_cases, 2):
            print(f"{i}. Testing: {test_case['description']}")
            
            # Create a mock email record
            email_record = Email(
                gmail_id=f"test_status_{i}_{datetime.now().timestamp()}",
                sender_email=f"recruiter@teststatus.com",
                sender_name="Test Recruiter",
                subject=f"Test Email - {test_case['email_type']}",
                body=f"This is a test email for {test_case['email_type']}",
                snippet=f"Test {test_case['email_type']}",
                received_at=datetime.utcnow(),
                email_type=test_case['email_type'],
                classification_confidence=0.95,
                is_matched=True,
                application_id=test_app.id
            )
            
            # Get current status before update
            db.refresh(test_app)
            status_before = test_app.status
            
            # Update status using the processor method
            processor._update_application_status(db, test_app, test_case['email_type'])
            db.commit()
            db.refresh(test_app)
            
            status_after = test_app.status
            
            # Verify status update
            if status_after == test_case['expected_status']:
                print(f"   ✓ Status updated correctly")
                print(f"   - Before: {status_before.value}")
                print(f"   - After: {status_after.value}")
            else:
                print(f"   ✗ Status update failed!")
                print(f"   - Expected: {test_case['expected_status'].value}")
                print(f"   - Got: {status_after.value}")
            
            print()
        
        # Test edge cases
        print(f"{len(test_cases) + 2}. Testing edge cases...")
        
        # Test: follow_up shouldn't change status
        db.refresh(test_app)
        test_app.status = ApplicationStatus.INTERVIEW
        db.commit()
        status_before = test_app.status
        
        processor._update_application_status(db, test_app, "follow_up")
        db.commit()
        db.refresh(test_app)
        
        if test_app.status == status_before:
            print("   ✓ follow_up email doesn't change status (correct)")
        else:
            print(f"   ✗ follow_up changed status from {status_before.value} to {test_app.status.value}")
        
        # Test: rejection shouldn't be overwritten by offer
        test_app.status = ApplicationStatus.REJECTED
        db.commit()
        status_before = test_app.status
        
        processor._update_application_status(db, test_app, "offer")
        db.commit()
        db.refresh(test_app)
        
        if test_app.status == ApplicationStatus.REJECTED:
            print("   ✓ Rejected status not overwritten by offer (correct)")
        else:
            print(f"   ✗ Rejected status was changed to {test_app.status.value}")
        
        print()
        
        # Clean up
        print("Cleaning up test data...")
        db.delete(test_app)
        db.commit()
        print("   ✓ Test data cleaned up")
        
        print()
        print("=" * 60)
        print("✓ Status update tests completed!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == '__main__':
    test_status_updates()

