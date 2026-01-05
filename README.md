Email Tracker to learn Backend Engineering (Job Application CRM)

An automated backend service that bridges the gap between your Gmail inbox and your job search tracking. This system fetches recruiter emails, uses AI to classify their intent, and automatically updates the status of your applications.

## 🤖 The Automation Pipeline

The system operates as a data refinery, moving raw communication from Gmail into structured, actionable insights.

**Gmail Inbox** (Targeted Fetching via Keywords)
&nbsp;&nbsp;&nbsp;&nbsp; ⬇️
**Deduplication Engine** (Checks `gmail_id` to prevent double-processing)
&nbsp;&nbsp;&nbsp;&nbsp; ⬇️
**AI Classification** (LLM interprets intent: *Interview, Rejection, Offer, etc.*)
&nbsp;&nbsp;&nbsp;&nbsp; ⬇️
**Relational Matcher** (Links email to the correct Application via domain extraction)
&nbsp;&nbsp;&nbsp;&nbsp; ⬇️
**Status Progression** (Autonomously moves Application Status forward)
&nbsp;&nbsp;&nbsp;&nbsp; ⬇️
**Persistent Storage** (Finalizes database transaction and audit trail)

---
