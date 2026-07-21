"""
Module: auth.py
Handles Spotify authentication using refresh tokens.
Automatically refreshes access tokens when expired.
"""

import os
from base64 import b64encode
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)

CLIENT_ID: str = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET: str = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN: str = os.environ["SPOTIFY_REFRESH_TOKEN"]


class SpotifyAuth:
    """Class to handle Spotify authentication"""

    def __init__(self):
        """Load credentials from environment variables and initialize"""
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.refresh_token = REFRESH_TOKEN
        self._access_token = None

    def refresh_access_token(self) -> str:
        """Request and refresh access token using refresh_token"""
        url = "https://accounts.spotify.com/api/token"

        auth_str = f"{self.client_id}:{self.client_secret}"
        headers = {
            "Authorization": "Basic " + b64encode(auth_str.encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        res = requests.post(url, headers=headers, data=data, timeout=10)
        res.raise_for_status()

        self._access_token = res.json()["access_token"]
        print("✅ : Access token refreshed")
        return self._access_token

    @property
    def token(self) -> str:
        """Return the current access token (refresh if not available)"""
        if not self._access_token:
            return self.refresh_access_token()
        return self._access_token


if __name__ == "__main__":
    auth = SpotifyAuth()
    print("✅ : Auth object created")

    token = auth.token
    print("✅ : Access token retrieved successfully")
