# app/models/email.py
from sqlalchemy import Column, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

class Email(Base):
    """
    Database model for job application emails
    Represents the 'emails' table
    """
    __tablename__ = "emails"
    
    # Primary key - unique ID for each email
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Gmail message ID - unique identifier from Gmail
    gmail_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Sender information
    sender_email = Column(String(255), nullable=False, index=True)
    sender_name = Column(String(255), nullable=True)
    
    # Email content
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    snippet = Column(Text, nullable=True)  # Short preview
    
    # Timestamp
    received_at = Column(DateTime, nullable=False, index=True)
    
    # Relationship to application
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=True, index=True)
    
    # Classification fields
    email_type = Column(String(50), nullable=True)  # e.g., "interview_request", "rejection"
    classification_confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Matching status
    is_matched = Column(Boolean, default=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    application = relationship("Application", back_populates="emails")
    
    def __repr__(self):
        subject_preview = self.subject[:50] + "..." if len(self.subject) > 50 else self.subject
        return f"<Email from {self.sender_email} - {subject_preview}>"

