# Use to generate a long-term Graph API Explorer Key
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

SHORT_LIVED_TOKEN = str(input("Enter the short-lived token: "))
APP_ID = os.getenv("APP_ID") or os.getenv("THREADS_APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

if not APP_ID:
    print("❌ Error: APP_ID or THREADS_APP_ID not found in .env")
    print(f"💡 Looking for .env at: {env_path}")
    print(f"💡 Make sure your .env file contains either APP_ID or THREADS_APP_ID")
    exit(1)

if not APP_SECRET:
    print("❌ Error: APP_SECRET not found in .env")
    print("💡 Get it from: Meta Developer Dashboard → Settings → Basic → App Secret")
    exit(1)

url = f"https://graph.facebook.com/v24.0/oauth/access_token"
params = {
    "grant_type": "fb_exchange_token",
    "client_id": APP_ID,
    "client_secret": APP_SECRET,
    "fb_exchange_token": SHORT_LIVED_TOKEN
}

print(f"🔄 Exchanging token...")
print(f"📝 Using APP_ID: {APP_ID[:10]}...")
response = requests.get(url, params=params)
data = response.json()

if "error" in data:
    print(f"❌ Error: {data['error']['message']}")
    print(f"📋 Full response: {data}")
else:
    long_lived_token = data.get("access_token")
    expires_in = data.get("expires_in", "unknown")
    print(f"✅ Long-lived token generated!")
    print(f"📝 Token expires in: {expires_in} seconds (~{int(expires_in)/86400:.1f} days)")
    print(f"\n🔑 Your long-lived token:")
    print(f"{long_lived_token}")
    print(f"\n💡 Add this to your .env file as THREADS_ACCESS_TOKEN")