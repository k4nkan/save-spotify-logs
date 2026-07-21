# Save Spotify Logs to Supabase 🎧

This repository fetches your recent Spotify listening history and saves it to a Supabase database.

- Fetches the latest tracks you played on Spotify.
- Stores track name, artist, playback time, and a save timestamp in Supabase.
- Automatically runs periodically via GitHub Actions (for typical use cases).
- Uses a Spotify **refresh token** to maintain long-term access.

---

## How to Get Refresh Token

Register this Redirect URI in the Spotify Developer Dashboard:

```text
http://[::1]:5000/callback
```

Then run:

```bash
python tools/get_refresh_token.py
```

Open the printed URL, approve the app, and copy the printed `SPOTIFY_REFRESH_TOKEN` to `.env`.

---

## How to Run 🏃

1.  **Get Spotify API Credentials:**
    Create an application on the Spotify Developer Dashboard to obtain your **Client ID** and **Client Secret**.

2.  **Set Environment Variables:**
    Copy the example environment file and fill in your credentials:

    ```bash
    cp .env.example .env
    ```

    Configure the following in your `.env` file:

    - `SPOTIFY_CLIENT_ID`: Your Spotify Application's Client ID.
    - `SPOTIFY_CLIENT_SECRET`: Your Spotify Application's Client Secret.
    - `SPOTIFY_REFRESH_TOKEN`: The refresh token for accessing the Spotify API (see "How to Get Refresh Token" above).
    - `SUPABASE_URL`: Your target Supabase project URL.
    - `SUPABASE_KEY`: The Supabase service role key or Anon Public Key with write permissions.

3.  **Install Dependencies:**
    Install the project's required Python packages.

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    ```

4.  **Execute the Script:**
    Run the main script. It will automatically handle token refresh using `auth.py`.

    ```bash
    python scripts/save_spotify_logs.py
    ```

This process will save tracks played within the **last hour** to the `spotify-playback-history` table (and upsert tracks to `spotify-tracks`) in your Supabase database.

GitHub Actions runs this script hourly and retries it up to 3 times on failure.
