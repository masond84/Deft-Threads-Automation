# Web API Setup Guide

## Prerequisites

1. **Supabase Account** (Free tier)
   - Go to https://supabase.com
   - Create a new project
   - Get your project URL and anon key

2. **Gmail App Password**
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate an app password for "Mail"
   - Save this password (you'll need it)

3. **Vercel Account** (Free tier)
   - Go to https://vercel.com
   - Sign up/login with GitHub

## Step 1: Set Up Supabase Database

1. In your Supabase project, go to SQL Editor
2. Run this SQL to create the table:

```sql
CREATE TABLE pending_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_text TEXT NOT NULL,
    mode VARCHAR(20) NOT NULL,
    metadata JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    published_at TIMESTAMP,
    thread_id VARCHAR(255),
    thread_url TEXT
);

-- Create index for faster queries
CREATE INDEX idx_pending_posts_status ON pending_posts(status);
CREATE INDEX idx_pending_posts_created_at ON pending_posts(created_at DESC);
```

3. Copy your Supabase URL and anon key from Settings > API

## Step 2: Update Environment Variables

Add these to your `.env` file:

```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here

# Email
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
NOTIFICATION_EMAIL=your-email@gmail.com

# App URL (update after deployment)
APP_BASE_URL=https://your-app.vercel.app
```

## Step 3: Deploy to Vercel

1. Install Vercel CLI (if not already):
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. In your project directory, run:
   ```bash
   vercel
   ```

4. Follow the prompts:
   - Link to existing project or create new
   - Set environment variables in Vercel dashboard:
     - All your existing `.env` variables
     - Plus the new ones (SUPABASE_URL, SUPABASE_KEY, GMAIL_ADDRESS, etc.)

5. Deploy:
   ```bash
   vercel --prod
   ```

6. Copy your deployment URL and update `APP_BASE_URL` in Vercel environment variables

## Step 4: Test the API

### Test Generation Endpoint

```bash
# Path A: Generate from briefs
curl -X POST https://your-app.vercel.app/api/generate/briefs \
  -H "Content-Type: application/json" \
  -d '{"limit": 1}'

# Path B: Generate from analysis
curl -X POST https://your-app.vercel.app/api/generate/analysis \
  -H "Content-Type: application/json" \
  -d '{"limit": 25}'

# Path C: Generate connection post
curl -X POST https://your-app.vercel.app/api/generate/connection \
  -H "Content-Type: application/json" \
  -d '{"connection_type": "founders"}'
```

### Test Approval Flow

1. Visit `https://your-app.vercel.app` to see pending posts
2. Click on a post to approve/reject
3. Or use the email links

## Step 5: Set Up Automation (Make.com/Zapier)

### Make.com Webhook

1. Create a new scenario in Make.com
2. Add "Webhooks" > "Custom webhook" trigger
3. Copy the webhook URL
4. In Make.com, add HTTP module:
   - Method: POST
   - URL: `https://your-app.vercel.app/api/generate/briefs`
   - Body: `{"limit": 1, "status_filter": "Ready"}`
   - Headers: `Content-Type: application/json`

### Scheduled Automation

Use Make.com's "Schedule" module to trigger generation at specific times.

## Troubleshooting

### Email Not Sending
- Verify Gmail app password is correct
- Check Gmail account has 2FA enabled
- Verify `NOTIFICATION_EMAIL` is set correctly

### Database Errors
- Verify Supabase URL and key are correct
- Check table was created successfully
- Verify RLS (Row Level Security) policies allow access

### API Errors
- Check Vercel function logs
- Verify all environment variables are set
- Check that dependencies are in requirements.txt

## Local Testing

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn api.index:app --reload --port 8000
```

Then visit `http://localhost:8000` to test the web UI.



