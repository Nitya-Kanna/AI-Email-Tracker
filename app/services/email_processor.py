"""
Email Processor Service

Orchestrates the workflow of:
1. Fetching emails from Gmail
2. Classifying emails with AI
3. Storing emails in database
4. Matching emails to applications
"""
import re
from typing import List, Dict, Optional
from datetime import datetime

from app.database import SessionLocal
from app.models.email import Email
from app.models.application import Application
from app.services.gmail_service import GmailService
from app.services.email_classifier import EmailClassifier


class EmailProcessor:
    """
    Processes emails: fetches, classifies, stores, and matches to applications
    """
    
    def __init__(self):
        """Initialize email processor with Gmail and Classifier services"""
        self.gmail_service = GmailService()
        self.classifier = EmailClassifier()
    
    def process_emails_from_companies(self, company_keywords: List[str], max_results: int = 50) -> Dict[str, any]:
        """
        Process emails from specific companies
        
        Args:
            company_keywords: List of company keywords (e.g., ["meta", "google", "anthropic"])
            max_results: Maximum number of emails to process per company
            
        Returns:
            Dictionary with processing results:
            - total_fetched: Number of emails fetched
            - total_classified: Number of emails classified
            - total_stored: Number of emails stored in database
            - total_matched: Number of emails matched to applications
            - emails: List of processed email data
        """
        # Fetch emails from companies
        gmail_emails = self.gmail_service.search_from_companies(company_keywords)
        
        if not gmail_emails:
            return {
                "total_fetched": 0,
                "total_classified": 0,
                "total_stored": 0,
                "total_matched": 0,
                "emails": []
            }
        
        db = SessionLocal()
        try:
            results = self._process_gmail_list(gmail_emails, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Error processing emails: {e}")
        finally:
            db.close()
        
        return {
            "total_fetched": len(gmail_emails),
            "total_classified": len(results['processed_emails']),
            "total_stored": results['stored_count'],
            "total_matched": results['matched_count'],
            "emails": results['processed_emails']
        }
    
    def process_emails_from_query(self, query: str, max_results: int = 50) -> Dict[str, any]:
        """
        Process emails matching a Gmail search query
        
        Args:
            query: Gmail search query (e.g., "from:meta.com", "subject:interview")
            max_results: Maximum number of emails to process
            
        Returns:
            Dictionary with processing results (same format as process_emails_from_companies)
        """
        # Fetch emails
        gmail_emails = self.gmail_service.search(query, max_results=max_results)
        
        if not gmail_emails:
            return {
                "total_fetched": 0,
                "total_classified": 0,
                "total_stored": 0,
                "total_matched": 0,
                "emails": []
            }
        
        db = SessionLocal()
        try:
            results = self._process_gmail_list(gmail_emails, db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Error processing emails: {e}")
        finally:
            db.close()
        
        return {
            "total_fetched": len(gmail_emails),
            "total_classified": len(results['processed_emails']),
            "total_stored": results['stored_count'],
            "total_matched": results['matched_count'],
            "emails": results['processed_emails']
        }
    
    def _process_gmail_list(self, gmail_emails: List[Dict], db) -> Dict[str, any]:
        """
        Process a list of Gmail emails
        
        This is a helper method that contains the common processing logic
        used by both process_emails_from_companies and process_emails_from_query.
        
        Args:
            gmail_emails: List of email dictionaries from Gmail API
            db: Database session
            
        Returns:
            Dictionary with processing results:
            - processed_emails: List of processed email data
            - stored_count: Number of emails stored
            - matched_count: Number of emails matched to applications
        """
        processed_emails = []
        stored_count = 0
        matched_count = 0
        
        for gmail_email in gmail_emails:
            # Check if email already exists (by gmail_id)
            existing = db.query(Email).filter(
                Email.gmail_id == gmail_email['gmail_id']
            ).first()
            
            if existing:
                # Email already processed, skip
                continue
            
            # Get full email details
            try:
                full_email = self.gmail_service.get_message(gmail_email['gmail_id'])
            except Exception as e:
                print(f"Warning: Could not fetch full email {gmail_email['gmail_id']}: {e}")
                continue
            
            # Classify email
            classification = self.classifier.classify(
                subject=full_email['subject'],
                body=full_email['body'],
                sender=full_email['sender_email']
            )
            
            # Parse received date
            received_at = self._parse_email_date(full_email['date'])
            
            # Create email record
            email_record = Email(
                gmail_id=full_email['gmail_id'],
                sender_email=full_email['sender_email'],
                sender_name=full_email.get('sender_name'),
                subject=full_email['subject'],
                body=full_email['body'],
                snippet=full_email.get('snippet', ''),
                received_at=received_at,
                email_type=classification['email_type'],
                classification_confidence=classification['confidence'],
                is_matched=False
            )
            
            # Try to match to application
            application = self._match_to_application(db, full_email['sender_email'])
            if application:
                email_record.application_id = application.id
                email_record.is_matched = True
                matched_count += 1
                
                # Update application status based on email type
                self._update_application_status(db, application, classification['email_type'])
            
            # Store in database
            db.add(email_record)
            stored_count += 1
            
            processed_emails.append({
                "gmail_id": full_email['gmail_id'],
                "sender": full_email['sender_email'],
                "subject": full_email['subject'],
                "email_type": classification['email_type'],
                "confidence": classification['confidence'],
                "matched": email_record.is_matched,
                "application": application.company_name if application else None
            })
        
        return {
            "processed_emails": processed_emails,
            "stored_count": stored_count,
            "matched_count": matched_count
        }
    
    def _update_application_status(self, db, application: Application, email_type: str):
        """
        Update application status based on email type
        
        Status transitions:
        - interview_request/interview_scheduled → INTERVIEW (if APPLIED or SCREENING)
        - offer → OFFER (if not already REJECTED)
        - rejection → REJECTED
        - acknowledgment → SCREENING (if APPLIED)
        - follow_up → No change (or SCREENING if APPLIED)
        
        Args:
            db: Database session
            application: Application object
            email_type: Classified email type
        """
        from app.models.application import ApplicationStatus
        
        # Only update if status would move forward (not backward)
        current_status = application.status
        
        if email_type in ['interview_request', 'interview_scheduled']:
            # Move to interview stage
            if current_status in [ApplicationStatus.APPLIED, ApplicationStatus.SCREENING]:
                application.status = ApplicationStatus.INTERVIEW
        
        elif email_type == 'offer':
            # Move to offer stage (unless already rejected)
            if current_status != ApplicationStatus.REJECTED:
                application.status = ApplicationStatus.OFFER
        
        elif email_type == 'rejection':
            # Move to rejected
            application.status = ApplicationStatus.REJECTED
        
        elif email_type == 'acknowledgment':
            # Move to screening if still at applied
            if current_status == ApplicationStatus.APPLIED:
                application.status = ApplicationStatus.SCREENING
        
        # follow_up and other types don't change status
        # (they're just updates, not status changes)
    
    def _match_to_application(self, db, sender_email: str) -> Optional[Application]:
        """
        Match an email to an application based on company_keyword in email address
        
        Checks if company_keyword appears anywhere in the full email address
        (both username and domain parts).
        
        Args:
            db: Database session
            sender_email: Email address of sender (e.g., "recruiter@meta.com" or "learningusesv@gmail.com")
            
        Returns:
            Matching Application or None if no match found
        """
        if not sender_email or '@' not in sender_email:
            return None
        
        # Convert to lowercase for case-insensitive matching
        sender_email_lower = sender_email.lower()
        
        # Get all applications and check if their keyword appears in the email address
        all_applications = db.query(Application).all()
        
        for app in all_applications:
            keyword = app.company_keyword.lower()
            # Check if keyword appears anywhere in the email address
            if keyword in sender_email_lower:
                return app
        
        return None
    
    def _extract_domain_keyword(self, email: str) -> Optional[str]:
        """
        Extract domain keyword from email address
        
        Examples:
        - "recruiter@meta.com" -> "meta"
        - "hr@anthropic.com" -> "anthropic"
        - "noreply@google.com" -> "google"
        
        Args:
            email: Email address
            
        Returns:
            Domain keyword or None
        """
        # Extract domain part
        if '@' not in email:
            return None
        
        domain = email.split('@')[1].lower()
        
        # Remove common TLDs and subdomains
        # e.g., "meta.com" -> "meta", "careers.google.com" -> "google"
        domain_parts = domain.split('.')
        
        # Remove TLD (last part)
        if len(domain_parts) > 1:
            domain_parts = domain_parts[:-1]
        
        # Get the main domain keyword (usually the last meaningful part)
        # Handle cases like "careers.google.com" -> "google"
        # or "noreply.meta.com" -> "meta"
        for part in reversed(domain_parts):
            # Skip common prefixes
            if part not in ['www', 'mail', 'email', 'noreply', 'no-reply', 'careers', 'jobs', 'hr', 'recruiting', 'recruiter']:
                return part
        
        # If all parts were skipped, return the last part
        return domain_parts[-1] if domain_parts else None
    
    def _parse_email_date(self, date_string: str) -> datetime:
        """
        Parse email date string to datetime object
        
        Args:
            date_string: Email date string from Gmail API
            
        Returns:
            datetime object
        """
        from email.utils import parsedate_to_datetime
        
        try:
            # Try parsing with email.utils
            return parsedate_to_datetime(date_string)
        except (ValueError, TypeError):
            # Fallback to current time if parsing fails
            return datetime.utcnow()

