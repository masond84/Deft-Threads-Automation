# Threads Automation

Automated system for generating and posting content to Threads from Notion database briefs using OpenAI GPT.

## Features

- **Three Generation Modes**: Generate posts from Notion briefs, analyze past posts, or create connection posts
- **Web API**: REST API for automation (Make.com, Zapier, webhooks)
- **Mobile Approval**: Web-based approval interface works on any device
- **Email Notifications**: Get notified when posts are ready for approval
- **Notion Integration**: Fetches post briefs from your Notion database (Path A)
- **Style Analysis**: Analyzes your past Threads posts to match your authentic writing style (Path B)
- **Connection Posts**: Quick networking posts (Path C)
- **AI-Powered Generation**: Uses OpenAI GPT to generate custom posts based on briefs and brand profile
- **Brand Consistency**: Incorporates brand voice, tone, and style guidelines
- **Auto-Posting**: Publishes approved posts directly to Threads
- **Smart Content**: Ensures posts meet Threads requirements (max 500 chars, no emojis, complete CTAs)

## Prerequisites

- Python 3.8+
- Meta Developer Account with Threads API access
- Notion account with API access
- OpenAI API key
- A Notion database with post briefs

## Setup

### 1. Clone and Install Dependencies

#### Install required packages
pip install -r requirements.txt### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

#### Threads API Configuration
THREADS_ACCESS_TOKEN=your_threads_access_token_here
THREADS_APP_ID=your_app_id_here

#### Meta App Configuration (for long-lived token generation)
APP_ID=your_app_id_here
APP_SECRET=your_app_secret_here

#### Notion API Configuration
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

#### OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here### 3. Get Your API Credentials

#### Threads Access Token
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Generate a User Token with permissions:
   - `threads_basic`
   - `threads_content_publish`
4. Copy the token to `THREADS_ACCESS_TOKEN` in `.env`

**Note**: Short-lived tokens expire after ~1 hour. Implementing refresh / token logic implementation later.

#### Notion API Key
1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the "Internal Integration Token" to `NOTION_API_KEY`
4. Share your database with the integration

#### OpenAI API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy to `OPENAI_API_KEY`

### 4. Configure Brand Profile (Optional)

Edit `src/config/brand_profile.md` with your brand guidelines:
- Brand voice and tone
- Target audience
- Content style preferences
- Example posts

## Usage

The system supports two generation modes:

- **Path A: Notion Briefs** (Default) - Generate posts from your Notion database briefs
- **Path B: Post Analysis** - Generate posts by analyzing your past Threads posts to match your style

---

### Path A: Notion Briefs (Default Mode)

Generates posts from your Notion database briefs. Uses brief content + brand profile.

#### Basic Usage

```bash
python scripts/generate_and_post.py --mode briefs --limit 5
```

**What happens:**
1. Fetches 5 briefs from Notion
2. Generates a post for each brief using GPT + brand profile
3. Shows preview of all generated posts
4. Asks for approval for each post
5. Posts approved content to Threads

#### With Status Filter

```bash
python scripts/generate_and_post.py --mode briefs --limit 5 --status "Ready"
```

**What happens:**
- Only fetches briefs with status "Ready"
- Useful for filtering by workflow stage

#### Auto-Approve (Use with Caution)

```bash
python scripts/generate_and_post.py --mode briefs --limit 3 --auto-approve
```

**What happens:**
- Skips individual approval prompts
- Still asks for final confirmation before posting
- Useful for batch processing

#### Custom Post Delay

```bash
python scripts/generate_and_post.py --mode briefs --limit 5 --post-delay 120
```

**What happens:**
- Waits 120 seconds (2 minutes) between each post
- Default is 60 seconds

#### Default Mode (No Flag Needed)

```bash
python scripts/generate_and_post.py --limit 5
```

**What happens:**
- Same as `--mode briefs` (briefs is the default mode)

---

## Path B: Post Analysis Mode

Generates posts by analyzing your past Threads posts. Matches your writing style without needing Notion briefs.

#### Basic Usage (No Topic)

```bash
python scripts/generate_and_post.py --mode analysis --limit 25
```

**What happens:**
1. Fetches your last 25 posts from Threads
2. Analyzes patterns (openings, endings, structure, tone)
3. Generates a new post matching your style
4. Shows preview with analysis stats
5. Asks for approval
6. Posts if approved

**Example Output:**
```
📥 Fetching 25 past posts for analysis...
✅ Fetched 21 posts from Threads
📊 Analyzing post patterns...
🤖 Generating post...

📋 GENERATED POSTS PREVIEW
======================================================================
Post #1
──────────────────────────────────────────────────────────────────────
📊 Analysis: 20 posts analyzed
📏 Avg Length: 205 chars

💬 Generated Post (387 chars):
[Your style-matched post here]
```

#### With Specific Topic

```bash
python scripts/generate_and_post.py --mode analysis --limit 25 --topic "software development"
```

**What happens:**
- Analyzes your past posts for style
- Generates a post about "software development" in your style
- Useful when you want a specific topic but in your voice

#### More Posts for Better Analysis

```bash
python scripts/generate_and_post.py --mode analysis --limit 50
```

**What happens:**
- Analyzes more posts (up to 50)
- Better pattern detection if you have many posts
- More accurate style matching

---

## Path C: Connection Posts (Quick Networking)

Generates short, casual networking posts to connect with others in your space. Uses brand profile to understand your target audience.

### Basic Usage

python scripts/generate_and_post.py --mode connection**What happens:**
1. Uses brand profile to identify your target audience
2. Generates a short, casual connection post (100-200 chars)
3. Shows preview
4. Asks for approval
5. Posts if approved

---

## Comparison Table

| Feature | Path A (Briefs) | Path B (Analysis) |
|---------|----------------|-------------------|
| **Source** | Notion database | Your past Threads posts |
| **Content** | Based on brief topic | Style-matched, optional topic |
| **Use Case** | Planned content from briefs | Quick posts in your style |
| **Requires** | Notion briefs | Past posts on Threads |
| **Limit Parameter** | Number of briefs | Number of posts to analyze |
| **Topic Control** | From brief | Optional via `--topic` |

---

## Real-World Usage Examples

### Scenario 1: Daily Content from Briefs
```bash
# Generate 3 posts from "Ready" briefs
python scripts/generate_and_post.py --mode briefs --limit 3 --status "Ready"
```

### Scenario 2: Quick Style-Matched Post
```bash
# Generate a post about "API integration" in your style
python scripts/generate_and_post.py --mode analysis --limit 25 --topic "API integration"
```

### Scenario 3: Batch Posting with Delays
```bash
# Generate 5 posts from briefs, wait 2 minutes between posts
python scripts/generate_and_post.py --mode briefs --limit 5 --post-delay 120
```

### Scenario 4: Test Analysis Mode
```bash
# Just generate and preview, don't post (skip approval)
python scripts/generate_and_post.py --mode analysis --limit 25
# Then when asked to approve, say 'n' to skip posting
```

---

## Command-Line Options

### Common Options (Both Paths)

```bash
# Limit number of items to process
python scripts/generate_and_post.py --limit 5

# Auto-approve all posts (still requires final confirmation)
python scripts/generate_and_post.py --auto-approve

# Custom delay between posts (in seconds)
python scripts/generate_and_post.py --post-delay 120
```

### Path A Only Options

```bash
# Filter briefs by status
python scripts/generate_and_post.py --mode briefs --status "Ready"
```

### Path B Only Options

```bash
# Specify topic for analysis mode
python scripts/generate_and_post.py --mode analysis --topic "your topic here"
```

### Get Help

```bash
# See all available options
python scripts/generate_and_post.py --help
```

---

## Important Notes

### Default Mode
If you don't specify `--mode`, it defaults to `briefs`:
```bash
python scripts/generate_and_post.py --limit 5  # Same as --mode briefs
```

### Path B Requirements
- You need past posts on your Threads account
- Your access token needs `threads_basic` permission
- More posts = better style analysis

### Error Handling
- **Path A**: If no briefs found, exits with error
- **Path B**: If posts can't be fetched, exits with error (no fallback)

### Approval Process
- Both paths use the same approval flow
- You can approve/reject/skip each post
- Final confirmation before posting

---

## Quick Reference

```bash
# Path A - Most common
python scripts/generate_and_post.py --mode briefs --limit 5

# Path B - Style matching
python scripts/generate_and_post.py --mode analysis --limit 25

# Path B with topic
python scripts/generate_and_post.py --mode analysis --limit 25 --topic "your topic here"

# Help (see all options)
python scripts/generate_and_post.py --help
```

---

## Generate Long-Lived Token

To avoid frequent token expiration:

```bash
python scripts/generate_long_term_key.py
```

Enter your short-lived token when prompted. The script will generate a long-lived token (expires in ~60 days) that you can add to `THREADS_ACCESS_TOKEN` in your `.env` file.

### Test Individual Components

```bash
# Test posting a single thread
python scripts/post_thread.py "Your post text here"
```

---

## Web API & Mobile Approval

The system includes a web API and mobile-friendly approval interface for automation and remote access.

### Quick Start

1. **Set up Supabase** (free database)
   - Create project at https://supabase.com
   - Run SQL from `docs/SETUP_WEB_API.md` to create table

2. **Configure Email**
   - Set up Gmail app password
   - Add to `.env`: `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD`

3. **Deploy to Vercel**
   ```bash
   vercel
   ```
   - Set all environment variables in Vercel dashboard
   - Update `APP_BASE_URL` after deployment

4. **Access Web UI**
   - Visit your Vercel URL
   - Approve posts from any device

### API Endpoints

- `POST /api/generate/briefs` - Generate from Notion briefs
- `POST /api/generate/analysis` - Generate from post analysis
- `POST /api/generate/connection` - Generate connection post
- `GET /api/posts/pending` - Get all pending posts
- `GET /api/posts/{id}` - Get specific post
- `POST /api/posts/{id}/approve` - Approve a post
- `POST /api/posts/{id}/reject` - Reject a post
- `POST /api/posts/{id}/publish` - Publish approved post

See `docs/SETUP_WEB_API.md` for detailed setup instructions.

---

## Project Structure