Email Tracker to learn Backend Engineering (Job Application CRM)

An automated backend service that bridges the gap between your Gmail inbox and your job search tracking. This system fetches recruiter emails, uses AI to classify their intent, and automatically updates the status of your applications.

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

