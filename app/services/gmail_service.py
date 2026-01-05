"""
Gmail Service for fetching and searching emails via Gmail API

This service provides methods to search, fetch, and process emails from Gmail.
Authentication is handled by GmailAuthenticator.
"""
import os
import re
import base64
from typing import List, Dict, Optional
from datetime import datetime

from googleapiclient.errors import HttpError
from app.services.gmail_authenticator import GmailAuthenticator


class GmailService:
    """
    Service for interacting with Gmail API
    
    Provides methods to search and fetch emails.
    Uses GmailAuthenticator for authentication.
    """
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize Gmail service
        
        Args:
            credentials_path: Path to credentials.json (default: root directory)
            token_path: Path to token.json (default: root directory)
        """
        # Use authenticator for authentication
        self.authenticator = GmailAuthenticator(credentials_path, token_path)
        self.service = self.authenticator.get_service()
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search Gmail with any query string, and only searches the "from" field. 
        
        Args:
            query: Gmail search query (e.g., "from:example.com", "subject:interview")
            max_results: Maximum number of results to return
            
        Returns:
            List of email dictionaries with keys:
            - gmail_id: Gmail message ID
            - sender: Full sender string (e.g., "Name <email@domain.com>")
            - sender_email: Extracted email address
            - subject: Email subject
            - date: Email date string
            - snippet: Email preview snippet
        """
        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Fetch details for each email
            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                # Parse headers
                headers = message['payload'].get('headers', [])
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
                
                # Extract email address from sender
                sender_email = self._extract_email_address(sender)
                
                email_data = {
                    'gmail_id': message['id'],
                    'sender': sender,
                    'sender_email': sender_email,
                    'subject': subject,
                    'date': date,
                    'snippet': message.get('snippet', '')
                }
                
                emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as error:
            raise Exception(f"Error searching emails: {error}")
    
    def get_message(self, gmail_id: str) -> Dict:
        """
        Fetch full email message by Gmail ID
        
        Args:
            gmail_id: Gmail message ID
            
        Returns:
            Dictionary with full email data including:
            - gmail_id: Gmail message ID
            - sender: Full sender string
            - sender_email: Extracted email address
            - sender_name: Sender name (if available)
            - subject: Email subject
            - date: Email date string
            - body: Full email body (text and/or HTML)
            - snippet: Email preview snippet
            - headers: All email headers
        """
        try:
            # Get full message
            message = self.service.users().messages().get(
                userId='me',
                id=gmail_id,
                format='full'
            ).execute()
            
            # Parse headers
            headers = message['payload'].get('headers', [])
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
            
            # Extract sender details
            sender_email = self._extract_email_address(sender)
            sender_name = self._extract_sender_name(sender)
            
            # Extract body
            body_text, body_html = self._extract_body(message['payload'])
            
            email_data = {
                'gmail_id': message['id'],
                'sender': sender,
                'sender_email': sender_email,
                'sender_name': sender_name,
                'subject': subject,
                'date': date,
                'body': body_text or body_html or '',
                'body_html': body_html,
                'body_text': body_text,
                'snippet': message.get('snippet', ''),
                'headers': {h['name']: h['value'] for h in headers}
            }
            
            return email_data
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
        except Exception as error:
            raise Exception(f"Error fetching message: {error}")
    
    def search_from_companies(self, keywords: List[str]) -> List[Dict]:
        """
        Search for emails from specific companies by keyword
        
        Builds a query like: "from:meta OR from:google OR from:amazon"
        
        Args:
            keywords: List of company keywords (e.g., ["meta", "google", "amazon"])
            
        Returns:
            List of email dictionaries (same format as search())
        """
        if not keywords:
            return []
        
        # Build OR query for each keyword
        query_parts = [f"from:{keyword}" for keyword in keywords]
        query = " OR ".join(query_parts)
        
        # Use a higher max_results since we're searching multiple companies
        return self.search(query, max_results=100)
    
    def _extract_email_address(self, sender_string: str) -> str:
        """
        Extract email address from sender string
        
        Handles formats like:
        - "John Doe <john@company.com>" → "john@company.com"
        - "john@company.com" → "john@company.com"
        - "John Doe" → "John Doe" (if no email found)
        
        Args:
            sender_string: Full sender string from email header
            
        Returns:
            Extracted email address or original string if no email found
        """
        # Look for email in angle brackets
        match = re.search(r'<(.+?)>', sender_string)
        if match:
            return match.group(1).strip()
        
        # If no brackets, check if string is an email
        if '@' in sender_string:
            return sender_string.strip()
        
        # Return original if no email found
        return sender_string.strip()
    
    def _extract_sender_name(self, sender_string: str) -> Optional[str]:
        """
        Extract sender name from sender string
        
        Args:
            sender_string: Full sender string from email header
            
        Returns:
            Sender name or None if not found
        """
        # If format is "Name <email>", extract name
        match = re.match(r'^(.+?)\s*<', sender_string)
        if match:
            return match.group(1).strip().strip('"')
        
        # If no brackets and no @, might be just a name
        if '@' not in sender_string:
            return sender_string.strip()
        
        return None
    
    def _extract_body(self, payload: Dict) -> tuple:
        """
        Extract email body from message payload
        
        Args:
            payload: Message payload from Gmail API
            
        Returns:
            Tuple of (body_text, body_html)
        """
        body_text = None
        body_html = None
        
        def extract_from_part(part):
            """Recursively extract body from message parts"""
            nonlocal body_text, body_html
            
            if part.get('mimeType') == 'text/plain':
                data = part.get('body', {}).get('data')
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            elif part.get('mimeType') == 'text/html':
                data = part.get('body', {}).get('data')
                if data:
                    body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            # Recursively process nested parts
            if 'parts' in part:
                for subpart in part['parts']:
                    extract_from_part(subpart)
        
        extract_from_part(payload)
        
        return body_text, body_html

