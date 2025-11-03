# Save Spotify Logs to Supabase 🎧

This repository fetches your recent Spotify listening history and saves it to a Supabase database.

- Fetches the latest tracks you played on Spotify.
- Stores track name, artist, playback time, and a save timestamp in Supabase.
- Automatically runs periodically via GitHub Actions (for typical use cases).
- Uses a Spotify **refresh token** to maintain long-term access.

---

## How to Get Refresh Token

[Article](https://zenn.dev/litkyan/articles/0ee3dda9eef4bd)

---

## How to Run 🏃

1.  **Get Spotify API Credentials:**
    Create an application on the Spotify Developer Dashboard to obtain your **Client ID** and **Client Secret**.

2.  **Set Environment Variables:**
    Configure the following environment variables. These are essential for the scripts (`auth.py` and `save_spotify_logs.py`) to function.

    - `SPOTIFY_CLIENT_ID`: Your Spotify Application's Client ID.
    - `SPOTIFY_CLIENT_SECRET`: Your Spotify Application's Client Secret.
    - `SPOTIFY_REFRESH_TOKEN`: The refresh token for accessing the Spotify API (see "How to Get Refresh Token" above).
    - `SUPABASE_URL`: Your target Supabase project URL.
    - `SUPABASE_KEY`: The Supabase service role key or Anon Public Key with write permissions.

3.  **Install Dependencies:**
    Install the project's required Python packages.

    ```bash
    pip install requests python-dotenv supabase
    ```

4.  **Execute the Script:**
    Run the main script. It will automatically handle token refresh using `auth.py`.

    ```bash
    python save_spotify_logs.py
    ```

This process will save tracks played within the **last hour** to the `spotify-logs` table in your Supabase database.
