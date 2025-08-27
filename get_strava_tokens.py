import os
import json
import pathlib
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

DATA_DIR = pathlib.Path(__file__).resolve().parent / "data"
TOKENS_PATH = DATA_DIR / "strava_tokens.json"
DATA_DIR.mkdir(exist_ok=True)

def main():
    print("Open your browser and log in to Strava at this URL:\n")
    url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri=http://localhost/exchange_token"
        f"&approval_prompt=force"
        f"&scope=activity:read_all"
    )
    print(url, "\n")
    code = input("Paste the code from the redirect URL (after code=...): ").strip()

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    r = requests.post("https://www.strava.com/oauth/token", data=payload, timeout=30)
    r.raise_for_status()
    tokens = r.json()

    with open(TOKENS_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "obtained_at": tokens.get("created_at")
        }, f, indent=2)

    print(f"\nTokens saved to {TOKENS_PATH}")
    print("From now on, use only the refresh_token from that file. "
          "Your .env no longer needs STRAVA_REFRESH_TOKEN "
          "(it can be empty or removed).")

if __name__ == "__main__":
    main()
