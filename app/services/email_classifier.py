"""
Email Classifier Service using OpenAI

Classifies recruiter emails into categories like interview requests,
rejections, offers, etc. Includes rate limiting with tenacity.
"""
import json
import re
import time
import logging
from typing import Dict, Optional
from openai import OpenAI, RateLimitError, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.config import settings

# Set up logging for tenacity
logger = logging.getLogger(__name__)


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
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini", requests_per_minute: int = 50):
        """
        Initialize the email classifier
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY from config)
            model: OpenAI model to use (default: gpt-4o-mini)
            requests_per_minute: Maximum requests per minute (default: 50)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self.requests_per_minute = requests_per_minute
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. "
                "Please set it in your .env file or pass it as api_key parameter."
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Rate limiting: track request times (simple sliding window)
        self.request_times = []
    
    def _wait_for_rate_limit(self):
        """Simple rate limiting: wait if we're hitting the limit"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # If we've hit the limit, wait
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0]) + 0.1  # Small buffer
            if sleep_time > 0:
                time.sleep(sleep_time)
                # Clean up after waiting
                now = time.time()
                self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Record this request
        self.request_times.append(time.time())
    
    @retry(
        stop=stop_after_attempt(3),  # Retry up to 3 times
        wait=wait_exponential(multiplier=1, min=2, max=60),  # Exponential backoff: 2s, 4s, 8s...
        retry=retry_if_exception_type((RateLimitError, APIError)),  # Only retry on rate limit/API errors
        reraise=True  # Re-raise the exception if all retries fail
    )
    def _call_openai(self, prompt: str) -> Dict[str, any]:
        """
        Call OpenAI API with retry logic
        
        This method is wrapped with tenacity for automatic retries.
        """
        # Wait for rate limit before making request
        self._wait_for_rate_limit()
        
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
        return self._parse_response(result_text)
    
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
            # Call OpenAI with retry logic (handled by tenacity)
            result = self._call_openai(prompt)
            return result
            
        except (RateLimitError, APIError) as e:
            # If all retries failed, return fallback
            logger.warning(f"OpenAI API error after retries: {e}")
            return {
                "email_type": "other",
                "confidence": 0.0,
                "reasoning": f"API error after retries: {str(e)}"
            }
        except Exception as e:
            # Other errors - don't retry
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
