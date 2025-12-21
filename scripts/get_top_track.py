"""
Fetch and print the top 3 tracks on a specific date (JST).
"""

import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_top_tracks_on_date(date_str: str, limit_count: int = 3):
    """
    date_str: 'YYYY-MM-DD' (JST)
    Return top tracks on that date.
    """
    res = supabase.rpc(
        "top_tracks_on_date_jst",
        {
            "target_date": date_str,
            "limit_count": limit_count,
        },
    ).execute()

    return res.data or []


def main():
    """
    Fetch and print the top 3 tracks on a specific date.
    """
    date_str = input("Enter date (YYYY-MM-DD): ").strip()

    top_tracks = fetch_top_tracks_on_date(date_str, 3)

    if not top_tracks:
        print(f"No data found for {date_str}")
        return

    print(f"Top 3 tracks on {date_str} (JST):")
    for track in top_tracks:
        print(
            f"{track['rank']}. "
            f"{track['track_name']} - {track['artist_name']} "
            f"({track['play_count']} plays)"
            f"{track['image_url']}"
        )


if __name__ == "__main__":
    main()
