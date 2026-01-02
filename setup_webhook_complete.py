#!/usr/bin/env python3
"""
Complete webhook setup helper

This script helps you:
1. Get your Google Cloud project ID
2. Create Pub/Sub subscription
3. Set up Gmail watch
"""
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return output"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} completed")
            return result.stdout.strip()
        else:
            print(f"⚠️  {description} failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 60)
    print("Gmail Webhook Complete Setup")
    print("=" * 60)
    print()
    
    # Step 1: Get project ID
    print("Step 1: Getting Google Cloud Project ID...")
    project_id = run_command("gcloud config get-value project", "Get project ID")
    
    if not project_id or project_id == "No project set":
        print("\n❌ No Google Cloud project set!")
        print("Please run:")
        print("  gcloud config set project YOUR_PROJECT_ID")
        print()
        project_id = input("Or enter your project ID manually: ").strip()
        if not project_id:
            print("❌ Project ID required. Exiting.")
            return
    else:
        print(f"✓ Using project: {project_id}")
    
    topic_name = f"projects/{project_id}/topics/gmail-notifications"
    print(f"\nTopic name: {topic_name}")
    
    # Step 2: Check if topic exists
    print("\nStep 2: Verifying topic exists...")
    result = run_command(f"gcloud pubsub topics describe gmail-notifications", "Check topic")
    if not result:
        print("⚠️  Topic might not exist. Make sure you created it.")
        continue_setup = input("\nContinue anyway? (y/n): ").strip().lower()
        if continue_setup != 'y':
            return
    
    # Step 3: Get webhook URL
    print("\nStep 3: Webhook URL setup...")
    print("\nYou need a public URL for your webhook.")
    print("Options:")
    print("  1. Use ngrok (for local testing)")
    print("  2. Use your production server URL")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        print("\n📋 To use ngrok:")
        print("  1. Install: brew install ngrok")
        print("  2. Run: ngrok http 8000")
        print("  3. Copy the https URL (e.g., https://abc123.ngrok.io)")
        print()
        webhook_url = input("Enter your ngrok URL (or press Enter to skip): ").strip()
        if not webhook_url:
            print("⚠️  Skipping subscription creation. You can create it later with:")
            print(f"   gcloud pubsub subscriptions create gmail-webhook \\")
            print(f"     --topic=gmail-notifications \\")
            print(f"     --push-endpoint={webhook_url}/api/webhooks/gmail")
    else:
        webhook_url = input("Enter your production server URL: ").strip()
    
    if webhook_url:
        # Remove trailing slash
        webhook_url = webhook_url.rstrip('/')
        webhook_endpoint = f"{webhook_url}/api/webhooks/gmail"
        
        print(f"\nWebhook endpoint: {webhook_endpoint}")
        
        # Step 4: Create subscription
        print("\nStep 4: Creating Pub/Sub subscription...")
        create_cmd = f"""gcloud pubsub subscriptions create gmail-webhook \\
  --topic=gmail-notifications \\
  --push-endpoint={webhook_endpoint}"""
        
        print(f"\nRunning: {create_cmd}")
        result = run_command(create_cmd, "Create subscription")
        
        if result is not None:
            print("✓ Subscription created!")
        else:
            print("⚠️  Subscription might already exist or failed to create")
    
    # Step 5: Set up Gmail watch
    print("\n" + "=" * 60)
    print("Step 5: Setting up Gmail watch")
    print("=" * 60)
    print()
    print(f"Topic name: {topic_name}")
    print()
    
    proceed = input("Ready to set up Gmail watch? (y/n): ").strip().lower()
    if proceed == 'y':
        from app.services.gmail_watcher import GmailWatcher
        
        watcher = GmailWatcher()
        try:
            result = watcher.setup_watch(topic_name)
            
            print()
            print("=" * 60)
            print("✓ Gmail watch set up successfully!")
            print("=" * 60)
            print(f"Expiration: {result.get('expiration')}")
            print(f"History ID: {result.get('historyId')}")
            print()
            print("Gmail will now send notifications when new emails arrive!")
            print()
            print("⚠️  Note: Watch expires after 7 days.")
            print("   Run 'python setup_gmail_watch.py' to renew it.")
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            print("Make sure:")
            print("1. Your Pub/Sub topic exists")
            print("2. Gmail has permission to publish to it")
            print("3. Topic name format is correct")
    else:
        print("\nSkipped Gmail watch setup.")
        print("Run 'python setup_gmail_watch.py' when ready.")
    
    print()
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()

