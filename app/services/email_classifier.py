"""
Email Classifier Service using OpenAI

Classifies recruiter emails into categories like interview requests,
rejections, offers, etc.
"""
import json
import re
from typing import Dict, Optional
from openai import OpenAI
from app.config import settings


class EmailClassifier:
    """
    Classifies recruiter emails using OpenAI
    
    Categorizes emails into types like interview_request, rejection, offer, etc.
    """
    
    # Valid email types
    EMAIL_TYPES = [
        "interview_request",      # Request to schedule an interview
        "interview_scheduled",    # Interview has been scheduled
        "offer",                  # Job offer extended
        "rejection",              # Application rejected
        "acknowledgment",         # Application received/acknowledged
        "follow_up",              # Follow-up email
        "other"                   # Other/uncategorized
    ]
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize the email classifier
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY from config)
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Please set it in your .env file or pass it as api_key parameter."
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
    
    def classify(self, subject: str, body: str, sender: str = "") -> Dict[str, any]:
        """
        Classify an email using AI
        
        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address (optional, for context)
            
        Returns:
            Dictionary with:
            - email_type: One of the EMAIL_TYPES
            - confidence: Float between 0.0 and 1.0
            - reasoning: Brief explanation of classification
        """
        # Build prompt for OpenAI
        prompt = self._build_classification_prompt(subject, body, sender)
        
        try:
            # Get classification from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that classifies job application emails from recruiters. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for more consistent classifications
            )
            
            result_text = response.choices[0].message.content
            result = self._parse_response(result_text)
            
            return result
            
        except Exception as e:
            # Fallback to "other" if classification fails
            return {
                "email_type": "other",
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}"
            }
    
    def _build_classification_prompt(self, subject: str, body: str, sender: str) -> str:
        """
        Build the prompt for OpenAI to classify the email
        
        Args:
            subject: Email subject
            body: Email body
            sender: Sender email
            
        Returns:
            Formatted prompt string
        """
        # Truncate body if too long (OpenAI has token limits)
        max_body_length = 3000
        body_preview = body[:max_body_length] + "..." if len(body) > max_body_length else body
        
        prompt = f"""Classify the following job application email into one of these categories:
- interview_request: Request to schedule an interview or phone screen
- interview_scheduled: Interview has been scheduled with date/time
- offer: Job offer extended
- rejection: Application rejected or not moving forward
- acknowledgment: Application received, thank you, or confirmation
- follow_up: Follow-up email, status update, or reminder
- other: Anything that doesn't fit the above categories

Email Details:
Subject: {subject}
Sender: {sender}
Body: {body_preview}

Respond with a JSON object with these exact fields:
{{
    "email_type": "one of the categories above",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of why you chose this category"
}}"""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse OpenAI's response and extract classification
        
        Args:
            response_text: Raw response from OpenAI (should be JSON)
            
        Returns:
            Dictionary with email_type, confidence, and reasoning
        """
        try:
            # Parse JSON response
            result = json.loads(response_text)
            
            # Validate email_type
            email_type = result.get("email_type", "other")
            if email_type not in self.EMAIL_TYPES:
                email_type = "other"
            
            # Validate confidence (0.0 to 1.0)
            confidence = float(result.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))
            
            return {
                "email_type": email_type,
                "confidence": confidence,
                "reasoning": result.get("reasoning", "No reasoning provided")
            }
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback if parsing fails
            return {
                "email_type": "other",
                "confidence": 0.0,
                "reasoning": f"Failed to parse response: {str(e)}"
            }
