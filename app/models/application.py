# app/models/application.py
from sqlalchemy import Column, String, Text, Date, DateTime, Enum
from datetime import datetime
import uuid
import enum
from app.database import Base

class ApplicationStatus(str, enum.Enum):
    """Possible application statuses"""
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"

class Application(Base):
    """
    Database model for job applications
    Represents the 'applications' table
    """
    __tablename__ = "applications"
    
    # Primary key - unique ID for each application
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Company information
    company_name = Column(String(255), nullable=False, index=True)
    company_keyword = Column(String(255), nullable=False, index=True)
    
    # Job information
    role_title = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    
    # Application tracking
    applied_date = Column(Date, nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Application {self.company_name} - {self.role_title}>"