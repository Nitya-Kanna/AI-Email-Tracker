"""
Gmail Watcher Service for setting up push notifications
"""
from typing import List, Optional, Dict
from app.services.gmail_service import GmailService


class GmailWatcher:
    """
    Sets up Gmail push notifications via Google Cloud Pub/Sub
    """
    
    def __init__(self):
        """Initialize with Gmail service"""
        self.gmail_service = GmailService()
        self.service = self.gmail_service.service
    
    def setup_watch(
        self, 
        topic_name: str, 
        label_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Set up Gmail to send push notifications to Pub/Sub topic
        
        Args:
            topic_name: Google Cloud Pub/Sub topic name 
                       (format: projects/PROJECT_ID/topics/TOPIC_NAME)
            label_ids: Gmail labels to watch (default: ['INBOX'])
            
        Returns:
            Watch response with expiration time and historyId
        """
        if label_ids is None:
            label_ids = ['INBOX']  # Watch inbox by default
        
        watch_request = {
            'topicName': topic_name,
            'labelIds': label_ids
        }
        
        try:
            result = self.service.users().watch(
                userId='me',
                body=watch_request
            ).execute()
            
            return result
        except Exception as e:
            raise Exception(f"Failed to set up Gmail watch: {e}")
    
    def stop_watch(self) -> Dict:
        """
        Stop Gmail push notifications
        
        Returns:
            Stop response
        """
        try:
            result = self.service.users().stop(
                userId='me'
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to stop Gmail watch: {e}")