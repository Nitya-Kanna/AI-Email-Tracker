Email Tracker to learn Backend Engineering (Job Application CRM)

An automated backend service that bridges the gap between your Gmail inbox and your job search tracking. This system fetches recruiter emails, uses AI to classify their intent, and automatically updates the status of your applications.

Current Automation: 

Gmail Inbox (Targeted Fetching)$$\downarrow$$Deduplication Engine (Checks gmail_id vs Database to prevent double-billing and data noise)$$\downarrow$$AI Classification Node (LLM analyzes Subject/Body to determine intent: Interview, Rejection, or Offer)$$\downarrow$$Relational Matcher (Extracts domain keywords to link the email to the correct Job Application record)$$\downarrow$$Status Progression Logic (Updates Application Status autonomously based on conversation stage)$$\downarrow$$Persistent Storage (Finalizes DB transaction and updates the User Dashboard)

