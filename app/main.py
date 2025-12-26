# app/main.py
from fastapi import FastAPI
from app.database import Base, engine

# Create all database tables
# This looks at all models that inherit from Base
# and creates the corresponding database tables


# Create FastAPI application
app = FastAPI(
    title="Email Tracker API",
    description="Track job applications and match emails",
    version="1.0.0"
)

# Root endpoint - just to test it works
@app.get("/")
async def root():
    return {
        "message": "Email Tracker API is running!",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}