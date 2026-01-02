"""
Webhook endpoints for receiving Gmail push notifications
"""
import json
import base64
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Header
from app.services.email_processor import EmailProcessor
from app.database import SessionLocal
from app.models.application import Application

router = APIRouter()


def extract_sender_from_notification(notification_data: dict) -> Optional[str]:
    """
    Extract sender email from Gmail/Pub/Sub notification
    
    Args:
        notification_data: Parsed notification data
        
    Returns:
        Sender email address or None
    """
    # Gmail notifications structure can vary
    # Try to extract from different possible formats
    if 'emailAddress' in notification_data:
        return notification_data['emailAddress']
    
    if 'message' in notification_data:
        message = notification_data['message']
        if 'attributes' in message:
            attrs = message['attributes']
            if 'emailAddress' in attrs:
                return attrs['emailAddress']
    
    return None


@router.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    x_goog_channel_id: Optional[str] = Header(None),
    x_goog_channel_token: Optional[str] = Header(None),
    x_goog_message_number: Optional[str] = Header(None)
):
    """
    Receive Gmail push notifications from Google Cloud Pub/Sub
    
    Only processes emails from addresses matching your job applications
    """
    try:
        body = await request.json()
        
        # Handle Pub/Sub subscription verification
        if 'subscription' in body:
            return {"status": "verified"}
        
        # Parse Pub/Sub message
        if 'message' not in body:
            return {"status": "received", "message": "No message in notification"}
        
        message = body['message']
        
        # Decode notification data
        notification_data = {}
        if 'data' in message:
            try:
                decoded_data = base64.b64decode(message['data']).decode('utf-8')
                notification_data = json.loads(decoded_data)
            except Exception as e:
                print(f"Error decoding notification: {e}")
                return {"status": "error", "error": "Failed to decode notification"}
        
        # Extract sender email
        sender_email = extract_sender_from_notification(notification_data)
        
        if not sender_email:
            # If we can't extract sender, try processing recent emails
            # This is a fallback - ideally we'd have the sender in notification
            print("Warning: Could not extract sender from notification")
            return {"status": "skipped", "reason": "No sender in notification"}
        
        # Check if sender matches any of your applications
        db = SessionLocal()
        try:
            applications = db.query(Application).all()
            allowed_keywords = [app.company_keyword.lower() for app in applications]
            
            # Check if sender matches any application
            sender_lower = sender_email.lower()
            matches = any(keyword in sender_lower for keyword in allowed_keywords)
            
            if not matches:
                return {
                    "status": "skipped",
                    "reason": f"Sender {sender_email} not from tracked applications",
                    "sender": sender_email
                }
            
            # Process the email (only if it matches!)
            processor = EmailProcessor()
            results = processor.process_emails_from_query(
                query=f"from:{sender_email}",
                max_results=10  # Process recent emails from this sender
            )
            
            return {
                "status": "processed",
                "sender": sender_email,
                "emails_processed": results['total_stored'],
                "emails_matched": results['total_matched']
            }
        
        finally:
            db.close()
    
    except Exception as e:
        print(f"Webhook error: {e}")
        import traceback
        traceback.print_exc()
        # Return 200 to acknowledge (don't retry on our errors)
        return {"status": "error", "error": str(e)}


@router.get("/webhooks/gmail")
async def gmail_webhook_get():
    """Handle GET requests (Pub/Sub verification, health check)"""
    return {"status": "ready", "message": "Gmail webhook endpoint is active"}