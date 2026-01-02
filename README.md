# Threads Automation

Automated system for generating and posting content to Threads from Notion database briefs using OpenAI GPT. Includes web API, mobile-friendly approval interface, and email notifications.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Get API Credentials](#4-get-api-credentials)
  - [5. Configure Brand Profile (Optional)](#5-configure-brand-profile-optional)
- [Web App Setup](#web-app-setup)
  - [1. Set Up Supabase Database](#1-set-up-supabase-database)
  - [2. Configure Email](#2-configure-email)
  - [3. Deploy to Vercel](#3-deploy-to-vercel)
- [Usage](#usage)
  - [Command-Line Interface](#command-line-interface)
    - [Path A: Notion Briefs](#path-a-notion-briefs)
    - [Path B: Post Analysis](#path-b-post-analysis)
    - [Path C: Connection Posts](#path-c-connection-posts)
  - [Web Interface](#web-interface)
  - [API Endpoints (Webhooks)](#api-endpoints-webhooks)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## Features

- **Three Generation Modes**: Notion briefs, style analysis, or connection posts
- **Web API**: REST API for automation (Make.com, Zapier, webhooks)
- **Mobile Approval**: Web-based approval interface works on any device
- **Email Notifications**: Get notified when posts are ready for approval
- **Auto-Posting**: Publishes approved posts directly to Threads
- **Smart Content**: Ensures posts meet Threads requirements (max 500 chars, no emojis)

---

## Prerequisites

- Python 3.8+
- Node.js (for Vercel CLI)
- Meta Developer Account with Threads API access
- Notion account with API access
- OpenAI API key
- Supabase account (for web app)
- Gmail account (for email notifications)

---

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd Threads_Automation
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Threads API
THREADS_ACCESS_TOKEN=your_threads_access_token_here
THREADS_APP_ID=your_app_id_here

# Meta App (for long-lived tokens)
APP_ID=your_app_id_here
APP_SECRET=your_app_secret_here

# Notion API
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Supabase (for web app)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key_here

# Email (for web app)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
NOTIFICATION_EMAIL=your-email@gmail.com

# App URL (update after Vercel deployment)
APP_BASE_URL=https://your-app.vercel.app
```

### 4. Get API Credentials

#### Threads Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Generate a User Token with permissions:
   - `threads_basic`
   - `threads_content_publish`
4. Copy token to `THREADS_ACCESS_TOKEN` in `.env`

**Note**: Short-lived tokens expire after ~1 hour. Use `scripts/generate_long_term_key.py` for 60-day tokens.

#### Notion API Key

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy "Internal Integration Token" to `NOTION_API_KEY`
4. Share your database with the integration

#### OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy to `OPENAI_API_KEY`

### 5. Configure Brand Profile (Optional)

Edit `src/config/brand_profile.md` with your brand guidelines:
- Brand voice and tone
- Target audience
- Content style preferences
- Example posts

---

## Web App Setup

### 1. Set Up Supabase Database

1. Create project at [Supabase](https://supabase.com)
2. Go to SQL Editor
3. Run this SQL:

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

CREATE INDEX idx_pending_posts_status ON pending_posts(status);
CREATE INDEX idx_pending_posts_created_at ON pending_posts(created_at DESC);
```

4. Copy Supabase URL and anon key from Settings > API
5. Add to `.env` file

### 2. Configure Email

1. Go to Google Account settings
2. Enable 2-factor authentication
3. Generate an app password for "Mail"
4. Add to `.env`: `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`

### 3. Deploy to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (from project directory)
vercel

# Deploy to production
vercel --prod
```

**After deployment:**
1. Copy your Vercel URL from dashboard
2. Update `APP_BASE_URL` in Vercel environment variables (no trailing slash)
3. Add all environment variables in Vercel Dashboard > Settings > Environment Variables

See `docs/SETUP_WEB_API.md` for detailed deployment instructions.

---

## Usage

### Command-Line Interface

#### Path A: Notion Briefs

Generate posts from Notion database briefs.

```bash
# Basic usage
python scripts/generate_and_post.py --mode briefs --limit 5

# With status filter
python scripts/generate_and_post.py --mode briefs --limit 5 --status "Ready"

# Auto-approve (skips individual prompts)
python scripts/generate_and_post.py --mode briefs --limit 3 --auto-approve

# Custom delay between posts (seconds)
python scripts/generate_and_post.py --mode briefs --limit 5 --post-delay 120

# Default mode (briefs is default)
python scripts/generate_and_post.py --limit 5
```

**Options:**
- `--mode briefs` - Generate from Notion briefs (default)
- `--limit N` - Number of briefs to process
- `--status "Status"` - Filter briefs by status
- `--auto-approve` - Skip individual approval prompts
- `--post-delay N` - Delay between posts in seconds (default: 60)

#### Path B: Post Analysis

Generate posts by analyzing your past Threads posts to match your style.

```bash
# Basic usage (no topic)
python scripts/generate_and_post.py --mode analysis --limit 25

# With specific topic
python scripts/generate_and_post.py --mode analysis --limit 25 --topic "software development"

# More posts for better analysis
python scripts/generate_and_post.py --mode analysis --limit 50
```

**Options:**
- `--mode analysis` - Generate from style analysis
- `--limit N` - Number of past posts to analyze (default: 25)
- `--topic "topic"` - Optional topic for generated post

#### Path C: Connection Posts

Generate short networking posts.

```bash
# Basic usage
python scripts/generate_and_post.py --mode connection

# With connection type
python scripts/generate_and_post.py --mode connection --connection-type "founders"
```

**Options:**
- `--mode connection` - Generate connection post
- `--connection-type "type"` - Optional connection type (e.g., "founders", "developers")

#### Common Options

```bash
# See all options
python scripts/generate_and_post.py --help

# Generate long-lived token (60 days)
python scripts/generate_long_term_key.py

# Test posting a single thread
python scripts/post_thread.py "Your post text here"
```

### Web Interface

1. **Start local server:**
   ```bash
   python scripts/test_api_local.py
   ```
   Visit `http://localhost:8000`

2. **Generate posts:**
   - Click "+ Generate Post"
   - Choose mode (Connection, Analysis, or Briefs)
   - Fill in options
   - Click "Generate"

3. **Approve posts:**
   - Click "Review & Approve" on pending posts
   - Review post content
   - Click "✓ Approve" or "✗ Reject"
   - Approved posts can be published immediately

4. **Publish posts:**
   - Click "Retry Publishing" on approved posts
   - Click "📤 Publish to Threads"
   - Post will be published to your Threads profile

### API Endpoints (Webhooks)

All endpoints support webhooks for Make.com, Zapier, or custom automation.

#### Generation Endpoints

```bash
# Generate from Notion briefs
POST https://your-app.vercel.app/api/generate/briefs
Content-Type: application/json
Body: {"limit": 1, "status_filter": "Ready"}

# Generate from analysis
POST https://your-app.vercel.app/api/generate/analysis
Content-Type: application/json
Body: {"limit": 25, "topic": "optional topic"}

# Generate connection post
POST https://your-app.vercel.app/api/generate/connection
Content-Type: application/json
Body: {"connection_type": "founders"}
```

#### Management Endpoints

```bash
# Get pending posts
GET https://your-app.vercel.app/api/posts/pending

# Get specific post
GET https://your-app.vercel.app/api/posts/{post_id}

# Approve post
POST https://your-app.vercel.app/api/posts/{post_id}/approve

# Reject post
POST https://your-app.vercel.app/api/posts/{post_id}/reject

# Publish post
POST https://your-app.vercel.app/api/posts/{post_id}/publish
```

**Response Format:**
```json
{
  "id": "post-id",
  "post_text": "Generated post text",
  "mode": "briefs|analysis|connection",
  "status": "pending|approved|published|rejected",
  "created_at": "2026-01-01T00:00:00",
  "approval_url": "https://your-app.vercel.app/approve/{post_id}",
  "thread_id": "thread-id",
  "thread_url": "https://www.threads.net/t/{thread_id}/"
}
```

---

## Project Structure

```
Threads_Automation/
├── api/                    # FastAPI endpoints
│   ├── index.py           # Main API entry point
│   ├── generate.py        # Generation endpoints
│   ├── posts.py           # Post management endpoints
│   └── approve.py         # Approval endpoints
├── src/
│   ├── ai/                # OpenAI integration
│   ├── api/               # Threads API client
│   ├── automation/        # Post generation logic
│   ├── config/            # Brand profile
│   ├── database/          # Notion client
│   ├── storage/           # Supabase storage
│   └── utils/             # Utilities (email, analysis)
├── scripts/               # CLI scripts
│   ├── generate_and_post.py
│   ├── generate_long_term_key.py
│   ├── post_thread.py
│   └── test_api_local.py
├── web/                   # Web UI
│   ├── index.html
│   ├── approve.html
│   └── static/
├── docs/                  # Documentation
├── vercel.json           # Vercel deployment config
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables (not in git)
```

---

## Troubleshooting

### Token Expired
```bash
# Generate new long-lived token
python scripts/generate_long_term_key.py
```

### Database Connection Errors
- Verify Supabase URL and key in `.env`
- Check Supabase project is active
- Ensure table was created successfully

### Email Not Sending
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail
- Verify `NOTIFICATION_EMAIL` is set correctly

### API Errors
- Check Vercel function logs: `vercel logs`
- Verify all environment variables are set
- Check that dependencies are in `requirements.txt`

### Web UI Not Loading
- Ensure server is running: `python scripts/test_api_local.py`
- Check browser console for errors
- Verify `APP_BASE_URL` is set correctly (no trailing slash)

---

## Quick Reference

### CLI Commands

```bash
# Generate from briefs
python scripts/generate_and_post.py --mode briefs --limit 5

# Generate from analysis
python scripts/generate_and_post.py --mode analysis --limit 25

# Generate connection post
python scripts/generate_and_post.py --mode connection

# Start web server
python scripts/test_api_local.py

# Generate long-lived token
python scripts/generate_long_term_key.py
```

### Web URLs

- Local: `http://localhost:8000`
- Production: `https://your-app.vercel.app`
- API Docs: `https://your-app.vercel.app/docs`

---

## Support

For detailed setup instructions, see:
- `docs/SETUP_WEB_API.md` - Web app deployment guide
- `docs/API_IMPLEMENTATION_SUMMARY.md` - API documentation
- `docs/ARCHITECTURE_POST_ANALYSIS.md` - Post analysis architecture
