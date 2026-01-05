import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes - what permissions we need
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate with Gmail and return service"""
    creds = None

    # Get the directory where THIS script is saved
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Join that folder path with the filename
    credentials_path = os.path.join(base_dir, 'credentials.json')
        
    # Check if we have saved credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    
    return service

if __name__ == '__main__':
    print("Authenticating with Gmail...")
    service = authenticate_gmail()
    print("✓ Authentication successful!")
    print("✓ token.json saved for future use")