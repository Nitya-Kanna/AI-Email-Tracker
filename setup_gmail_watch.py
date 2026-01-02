#!/usr/bin/env python3
"""
Setup script for Gmail push notifications

Run this once to set up Gmail to send notifications to Pub/Sub
"""
from app.services.gmail_watcher import GmailWatcher

def setup():
    """Set up Gmail push notifications"""
    watcher = GmailWatcher()
    
    # Your Pub/Sub topic (format: projects/PROJECT_ID/topics/YOUR_TOPIC_NAME)
    # Example: "projects/my-project-12345/topics/gmail-notifications"
    topic_name = input("Enter your Pub/Sub topic name (projects/PROJECT_ID/topics/TOPIC_NAME): ").strip()
    
    if not topic_name:
        print("❌ Topic name is required")
        return
    
    print()
    print("Setting up Gmail watch...")
    try:
        result = watcher.setup_watch(topic_name)
        
        print()
        print("=" * 60)
        print("✓ Gmail watch set up successfully!")
        print("=" * 60)
        print(f"Expiration: {result.get('expiration')}")
        print(f"History ID: {result.get('historyId')}")
        print()
        print("Gmail will now send notifications to your Pub/Sub topic")
        print("when new emails arrive in your inbox.")
        print()
        print("Note: Watch expires after 7 days. You'll need to renew it.")
        
    except Exception as e:
        print(f"❌ Error setting up watch: {e}")
        print()
        print("Make sure:")
        print("1. Your Pub/Sub topic exists")
        print("2. Gmail has permission to publish to it")
        print("3. Topic name format is correct: projects/PROJECT_ID/topics/TOPIC_NAME")

if __name__ == '__main__':
    setup()

