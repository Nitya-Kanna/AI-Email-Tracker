# test_fetch_by_sender.py
import base64
from test_gmail_auth import authenticate_gmail

def fetch_emails_from_sender(sender_keyword, max_results=10):
    """
    Fetch emails from addresses containing a specific keyword
    
    Examples:
    - sender_keyword="meta" → emails from @meta.com, @metamail.com, etc.
    - sender_keyword="linkedin" → emails from @linkedin.com
    - sender_keyword="indeed" → emails from @indeed.com
    """
    service = authenticate_gmail()
    
    # Build query to search in sender's email address
    query = f"from:{sender_keyword}"
    
    print(f"Searching for emails from addresses containing: '{sender_keyword}'")
    print(f"Query: {query}\n")
    
    try:
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print(f"❌ No emails found from addresses containing '{sender_keyword}'\n")
            print("Try:")
            print("1. Check if you have emails from this sender in Gmail")
            print("2. Try a different keyword (e.g., 'gmail', 'company', 'noreply')")
            return []
        
        print(f"✓ Found {len(messages)} emails!\n")
        
        # Fetch details for each email
        emails = []
        for i, msg in enumerate(messages, 1):
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            # Parse email
            headers = message['payload']['headers']
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown')
            
            # Extract email address from sender (removes name)
            sender_email = extract_email_address(sender)
            
            email_data = {
                'id': message['id'],
                'from': sender,
                'sender_email': sender_email,
                'subject': subject,
                'date': date,
                'snippet': message.get('snippet', '')
            }
            
            emails.append(email_data)
            
            # Print
            print(f"{i}. From: {sender_email}")
            print(f"   Full: {sender}")
            print(f"   Subject: {subject}")
            print(f"   Date: {date}")
            print(f"   Preview: {email_data['snippet'][:80]}...")
            print()
        
        return emails
        
    except Exception as error:
        print(f"❌ Error: {error}")
        return []

def extract_email_address(sender_string):
    """
    Extract email address from sender string
    
    Examples:
    - "John Doe <john@company.com>" → "john@company.com"
    - "john@company.com" → "john@company.com"
    """
    import re
    
    # Look for email in angle brackets
    match = re.search(r'<(.+?)>', sender_string)
    if match:
        return match.group(1)
    
    # If no brackets, check if string is an email
    if '@' in sender_string:
        return sender_string.strip()
    
    return sender_string

if __name__ == '__main__':
    print("="*60)
    print("FETCH EMAILS BY SENDER KEYWORD")
    print("="*60)
    print()
    
    # Example 1: Fetch from linkedin
    print("TEST 1: Emails from LinkedIn")
    print("-"*60)
    emails = fetch_emails_from_sender("linkedin", max_results=2)
    
   