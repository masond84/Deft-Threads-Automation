# Threads Automation

Automated system for generating and posting content to Threads from Notion database briefs using OpenAI GPT.

## Features

- **Notion Integration**: Fetches post briefs from your Notion database
- **AI-Powered Generation**: Uses OpenAI GPT to generate custom posts based on briefs and brand profile
- **Brand Consistency**: Incorporates brand voice, tone, and style guidelines
- **Interactive Review**: Preview and approve posts before publishing
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

# Install required packages
pip install -r requirements.txt### 2. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

# Threads API Configuration
THREADS_ACCESS_TOKEN=your_threads_access_token_here
THREADS_APP_ID=your_app_id_here

# Meta App Configuration (for long-lived token generation)
APP_ID=your_app_id_here
APP_SECRET=your_app_secret_here

# Notion API Configuration
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here

# OpenAI API Configuration
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

### Basic Workflow

# Generate and review posts (interactive approval)
python scripts/generate_and_post.py --limit 5This will:
1. Fetch briefs from Notion
2. Generate posts using GPT
3. Show preview of all generated posts
4. Ask for approval for each post
5. Confirm before posting
6. Post approved content to Threads

### Command-Line Options

# Limit number of briefs to process
python scripts/generate_and_post.py --limit 3

# Filter by status
python scripts/generate_and_post.py --status "Ready"

# Auto-approve all posts (still requires final confirmation)
python scripts/generate_and_post.py --limit 5 --auto-approve

# Custom delay between posts (in seconds)
python scripts/generate_and_post.py --limit 3 --post-delay 120### Generate Long-Lived Token

To avoid frequent token expiration:

python scripts/generate_long_term_key.pyEnter your short-lived token when prompted. The script will generate a long-lived token (expires in ~60 days) that you can add to `THREADS_ACCESS_TOKEN` in your `.env` file.

### Test Individual Components

# Test posting a single thread
python scripts/post_thread.py "Your post text here"## Project Structure