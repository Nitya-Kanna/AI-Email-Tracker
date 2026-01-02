# Railway Deployment Guide

## Files Created for Deployment

✅ **Procfile** - Tells Railway how to run your app
✅ **Updated database.py** - Now supports both SQLite (local) and PostgreSQL (Railway)
✅ **.railwayignore** - Excludes unnecessary files from deployment

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

Make sure your code is committed to Git:

```bash
git add .
git commit -m "Prepare for Railway deployment"
```

### Step 2: Deploy to Railway

**Option A: Via Railway Dashboard (Easiest)**

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo" (connect your GitHub account if needed)
4. Select your `email-tracker` repository
5. Railway will automatically detect it's a Python app

**Option B: Via Railway CLI**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Step 3: Add PostgreSQL Database

1. In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` environment variable
3. Your app will automatically use it!

### Step 4: Set Environment Variables

In Railway dashboard, go to your service → "Variables" tab, add:

- `DATABASE_URL` - **Auto-set by Railway** (from PostgreSQL service)
- `OPENAI_API_KEY` - Your OpenAI API key
- `DEBUG` - Set to `False` (optional)

### Step 5: Upload Gmail Credentials

**Important**: Railway's file system is ephemeral. You have two options:

**Option A: Upload via Railway Dashboard (Temporary)**
1. Go to your service → "Settings" → "Source"
2. Upload `credentials.json` (this is temporary, will be lost on redeploy)

**Option B: Use Environment Variables (Recommended)**
- Convert `credentials.json` to environment variables
- Or use Railway's file system and regenerate `token.json` after each deploy

**For now, use Option A to get started.**

### Step 6: Run Database Migrations

After deployment, run migrations:

**Via Railway Dashboard:**
1. Go to your service → "Deployments"
2. Click on the latest deployment
3. Open "Shell" tab
4. Run: `alembic upgrade head`

**Via Railway CLI:**
```bash
railway run alembic upgrade head
```

### Step 7: Get Your Railway URL

1. In Railway dashboard, go to your service
2. Click "Settings" → "Generate Domain"
3. Copy your URL (e.g., `https://your-app-name.up.railway.app`)

### Step 8: Test Your Deployment

Visit your Railway URL:
- `https://your-app-name.up.railway.app/` - Should show API info
- `https://your-app-name.up.railway.app/health` - Should return `{"status": "healthy"}`
- `https://your-app-name.up.railway.app/api/webhooks/gmail` - Should return webhook status

### Step 9: Set Up Pub/Sub Subscription

Now that you have a public URL, create the Pub/Sub subscription:

```bash
gcloud pubsub subscriptions create gmail-webhook \
  --topic=gmail-notifications \
  --push-endpoint=https://your-app-name.up.railway.app/api/webhooks/gmail
```

Replace `your-app-name.up.railway.app` with your actual Railway URL.

### Step 10: Set Up Gmail Watch

Run locally (or create a Railway one-off command):

```bash
python setup_gmail_watch.py
```

When prompted, enter: `projects/YOUR_PROJECT_ID/topics/gmail-notifications`

### Step 11: Test the Complete Flow

1. Send yourself a test email from an address matching one of your applications
2. Check Railway logs to see if webhook was called
3. Check your database to verify email was processed

## Troubleshooting

### Database Connection Issues
- Make sure PostgreSQL service is added and connected
- Check that `DATABASE_URL` is set correctly
- Verify migrations ran: `railway run alembic upgrade head`

### Gmail Authentication Issues
- Make sure `credentials.json` is uploaded
- You may need to regenerate `token.json` after deployment
- Check Railway logs for authentication errors

### Webhook Not Receiving Requests
- Verify Railway URL is accessible
- Check Pub/Sub subscription is active
- Verify Gmail watch is set up
- Check Railway logs for incoming requests

### Environment Variables Not Working
- Make sure variables are set in Railway dashboard
- Redeploy after adding new variables
- Check variable names match exactly (case-sensitive)

## Important Notes

1. **Gmail Credentials**: Railway's file system is ephemeral. Consider:
   - Storing credentials in environment variables
   - Using a secrets manager
   - Regenerating `token.json` after each deploy

2. **Database**: Railway uses PostgreSQL. Your local SQLite database won't be used. You'll need to:
   - Re-add your applications via CLI or API
   - Or export/import data from local to Railway

3. **Watch Expiration**: Gmail watches expire after 7 days. Set up a reminder to renew:
   ```bash
   python setup_gmail_watch.py
   ```

4. **Logs**: Check Railway logs in the dashboard to debug issues

## Next Steps After Deployment

1. ✅ Test webhook endpoint
2. ✅ Set up Pub/Sub subscription
3. ✅ Set up Gmail watch
4. ✅ Test with real email
5. ✅ Monitor logs for any issues

## Need Help?

- Railway Docs: https://docs.railway.app
- Check Railway logs in dashboard
- Verify all environment variables are set
- Test endpoints manually with curl

