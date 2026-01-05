"""
Gmail Authentication Service

Handles OAuth authentication for Gmail API.
Separated from GmailService for better testability and production flexibility.
"""
import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'  # Needed for watch
]


class GmailAuthenticator:
    """
    Handles Gmail OAuth authentication
    
    Manages credentials loading, token refresh, and OAuth flow.
    Can be used by any service that needs Gmail API access.
    """
    
    def __init__(
        self, 
        credentials_path: Optional[str] = None, 
        token_path: Optional[str] = None
    ):
        """
        Initialize Gmail authenticator
        
        Args:
            credentials_path: Path to credentials.json (default: root directory)
            token_path: Path to token.json (default: root directory)
        """
        # Set default paths to root directory
        if credentials_path is None:
            credentials_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'credentials.json'
            )
        if token_path is None:
            token_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                'token.json'
            )
        
        self.credentials_path = credentials_path
        self.token_path = token_path
    
    def get_credentials(self) -> Credentials:
        """
        Get valid Gmail API credentials
        
        Handles:
        - Loading existing token
        - Refreshing expired token
        - Running OAuth flow if needed
        - Saving token for future use
        
        Returns:
            Valid Credentials object
            
        Raises:
            FileNotFoundError: If credentials.json is not found
            Exception: If authentication fails
        """
        creds = None
        
        # Check if credentials file exists
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_path}. "
                "Please download credentials.json from Google Cloud Console."
            )
        
        # Load existing token if available
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"Warning: Could not load token.json: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Could not refresh token: {e}")
                    creds = None
            
            if not creds:
                # Run OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next time
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Warning: Could not save token.json: {e}")
        
        return creds
    
    def get_service(self):
        """
        Get authenticated Gmail API service
        
        Returns:
            Gmail API service object
            
        Raises:
            Exception: If service creation fails
        """
        creds = self.get_credentials()
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            return service
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {e}")

