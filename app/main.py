# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api.webhooks import router as webhooks_router

# Create all database tables
# This looks at all models that inherit from Base
# and creates the corresponding database tables


# Create FastAPI application
app = FastAPI(
    title="Email Tracker API",
    description="Track job applications and match emails",
    version="1.0.0"
)

# Enable CORS for Pub/Sub webhooks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pub/Sub needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhooks_router, prefix="/api", tags=["webhooks"])

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