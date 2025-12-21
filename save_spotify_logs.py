"""
Save Spotify logs to Supabase.
"""

import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from supabase import Client, create_client

from auth import SpotifyAuth

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_recent_tracks(auth: SpotifyAuth):  # pylint: disable=redefined-outer-name
    """
    Fetch recent tracks from Spotify.
    """
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    headers = {"Authorization": f"Bearer {auth.token}"}
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    return res.json()["items"]


def upsert_track(track: dict):
    """
    Upsert track to Supabase.
    """
    album = track["album"]
    images = album.get("images", [])

    image_url = images[0]["url"] if images else None

    supabase.table("spotify-tracks").upsert(
        {
            "track_id": track["id"],
            "track_name": track["name"],
            "artist_name": track["artists"][0]["name"],
            "track_url": track["external_urls"]["spotify"],
            "image_url": image_url,
        },
        on_conflict="track_id",
    ).execute()


def insert_play_log(track_id: str, played_at: datetime):
    """
    Insert play log to Supabase.
    """
    supabase.table("spotify-playback-history").insert(
        {
            "track_id": track_id,
            "played_at": played_at.isoformat(),
        }
    ).execute()


def save_recent_logs(items):  # pylint: disable=redefined-outer-name
    """
    Save recent logs to Supabase.
    """
    for item in items:
        track = item["track"]
        played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))

        upsert_track(track)
        insert_play_log(track["id"], played_at)


if __name__ == "__main__":
    auth = SpotifyAuth()
    print("✅ Spotify auth loaded")

    items = fetch_recent_tracks(auth)
    print(f"✅ fetched {len(items)} tracks")

    save_recent_logs(items)
    print("✅ logs saved")
