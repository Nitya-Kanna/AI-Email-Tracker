#!/usr/bin/env python3
"""Test script to verify Application-Email relationship works"""

from datetime import datetime, date
from app.models.application import Application, ApplicationStatus
from app.models.email import Email

print("=" * 60)
print("Testing Application-Email Relationship")
print("=" * 60)

# 1. Create an Application object (in memory, not committed)
print("\n1. Creating Application...")
application = Application(
    company_name="Tech Corp",
    company_keyword="techcorp",
    role_title="Software Engineer",
    job_description="Build amazing software",
    applied_date=date.today(),
    status=ApplicationStatus.APPLIED
)
print(f"   Created: {application}")
print(f"   Application ID: {application.id}")

# 2. Create Email objects linked to that Application
print("\n2. Creating Email objects linked to Application...")
email1 = Email(
    gmail_id="gmail_msg_12345",
    sender_email="recruiter@techcorp.com",
    sender_name="Jane Recruiter",
    subject="Interview Request - Software Engineer Position",
    body="We would like to schedule an interview...",
    snippet="We would like to schedule an interview...",
    received_at=datetime.now(),
    application_id=application.id,
    email_type="interview_request",
    classification_confidence=0.95,
    is_matched=True
)
print(f"   Created: {email1}")

email2 = Email(
    gmail_id="gmail_msg_67890",
    sender_email="hr@techcorp.com",
    sender_name="HR Team",
    subject="Thank you for your application",
    body="We have received your application...",
    snippet="We have received your application...",
    received_at=datetime.now(),
    application_id=application.id,
    email_type="acknowledgment",
    classification_confidence=0.88,
    is_matched=True
)
print(f"   Created: {email2}")

# 3. Test the relationship by adding emails to application
print("\n3. Adding emails to application.emails collection...")
application.emails.append(email1)
application.emails.append(email2)
print(f"   Added {len(application.emails)} emails to application")

# 4. Query: application.emails
print("\n4. Testing relationship: application.emails")
print(f"   Number of emails: {len(application.emails)}")
print(f"   Emails list:")
for i, email in enumerate(application.emails, 1):
    print(f"      {i}. {email}")
    print(f"         - Sender: {email.sender_email}")
    print(f"         - Subject: {email.subject}")
    print(f"         - Type: {email.email_type}")
    print(f"         - Application ID: {email.application_id}")

# 5. Test reverse relationship: email.application
print("\n5. Testing reverse relationship: email.application")
print(f"   Email 1's application: {email1.application}")
print(f"   Email 1's application company: {email1.application.company_name if email1.application else 'None'}")
print(f"   Email 2's application: {email2.application}")
print(f"   Email 2's application role: {email2.application.role_title if email2.application else 'None'}")

# 6. Verify the relationship works both ways
print("\n6. Verifying bidirectional relationship...")
assert email1.application_id == application.id, "Email 1's application_id should match application.id"
assert email2.application_id == application.id, "Email 2's application_id should match application.id"
assert len(application.emails) == 2, "Application should have 2 emails"
assert email1.application == application, "Email 1 should reference the application"
assert email2.application == application, "Email 2 should reference the application"
print("   ✓ All relationship checks passed!")

print("\n" + "=" * 60)
print("Relationship test completed successfully!")
print("=" * 60)
print("\nNote: Objects were created in memory only, not committed to database.")

