Email Tracker to learn Backend Engineering (Job Application CRM)

This will extend to a Job Application CRM project.

An automated backend service that bridges the gap between your Gmail inbox and your job search tracking. This system fetches recruiter emails, uses AI to classify their intent, and automatically updates the status of your applications.

Concepts Applied: 

- OAuth 2.0 login/authorization flow with Google
- Gmail API integration and webhook-based event processing
- Batch API requests for performance optimization
- FastAPI backend design (routing, CORS, health endpoints)
- SQLAlchemy data modeling, relationships, and Alembic migrations
- Transaction-safe database operations (commit/rollback patterns)
- AI-powered email classification using OpenAI APIs
- Retry, backoff, and rate-limiting patterns for external services
- Workflow/state-machine based processing for complex pipelines
- Deduplication, matching logic, and status transition rules

## 🤖 The Automation Pipeline

The system operates as a data refinery, moving raw communication from Gmail into structured, actionable insights.


1. **Gmail Inbox**  
   *Targeted fetching via keywords*

   ⬇️

2. **Deduplication Engine**  
   *Checks `gmail_id` to prevent double-processing*

   ⬇️

3. **AI Classification**  
   *LLM interprets intent: Interview, Rejection, Offer, etc.*

   ⬇️

4. **Relational Matcher**  
   *Links email to the correct application via domain extraction*

   ⬇️

5. **Status Progression**  
   *Autonomously moves application status forward*

   ⬇️

6. **Persistent Storage**  
   *Finalizes database transaction and audit trail*

