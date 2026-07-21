"""
Get a Spotify refresh token for this project.
"""

import os
import secrets
import socket
from base64 import b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://[::1]:5000/callback"
SCOPE = "user-read-recently-played"
STATE = secrets.token_urlsafe(24)


class IPv6HTTPServer(HTTPServer):
    """
    HTTP server bound to IPv6 localhost.
    """

    address_family = socket.AF_INET6


class CallbackHandler(BaseHTTPRequestHandler):
    """
    Handle Spotify authorization callback.
    """

    server: IPv6HTTPServer

    def do_GET(self):  # pylint: disable=invalid-name
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/callback":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        params = parse_qs(parsed_url.query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            self.server.auth_error = error
            self._write_response(
                400, "Spotify authorization failed. Check the terminal."
            )
            return

        if not code or state != STATE:
            self.server.auth_error = "missing code or invalid state"
            self._write_response(400, "Invalid callback. Check the terminal.")
            return

        self.server.auth_code = code
        self._write_response(200, "Refresh token received. You can close this window.")

    def log_message(self, format_value, *args):  # pylint: disable=redefined-builtin
        return

    def _write_response(self, status_code: int, message: str):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))


def require_env(name: str, value: str | None) -> str:
    """
    Return an environment variable value or stop with a clear error.
    """
    if value:
        return value

    raise RuntimeError(f"{name} is missing. Set it in {ROOT_DIR / '.env'}")


def build_auth_url() -> str:
    """
    Build Spotify authorization URL.
    """
    query = urlencode(
        {
            "response_type": "code",
            "client_id": require_env("SPOTIFY_CLIENT_ID", CLIENT_ID),
            "scope": SCOPE,
            "redirect_uri": REDIRECT_URI,
            "state": STATE,
            "show_dialog": "true",
        }
    )
    return f"https://accounts.spotify.com/authorize?{query}"


def exchange_code_for_refresh_token(code: str) -> str:
    """
    Exchange authorization code for a refresh token.
    """
    client_id = require_env("SPOTIFY_CLIENT_ID", CLIENT_ID)
    client_secret = require_env("SPOTIFY_CLIENT_SECRET", CLIENT_SECRET)
    auth_str = f"{client_id}:{client_secret}"

    headers = {
        "Authorization": "Basic " + b64encode(auth_str.encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=headers,
        data=data,
        timeout=10,
    )
    res.raise_for_status()

    refresh_token = res.json().get("refresh_token")
    if not refresh_token:
        raise RuntimeError("Refresh token was not returned by Spotify")

    return refresh_token


def main():
    """
    Print auth URL, wait for callback, and print refresh token.
    """
    auth_url = build_auth_url()

    print("Open this URL in your browser:")
    print(auth_url)
    print("")
    print(f"Waiting for callback on {REDIRECT_URI} ...")

    server = IPv6HTTPServer(("::1", 5000), CallbackHandler)
    server.auth_code = None
    server.auth_error = None
    server.handle_request()
    server.server_close()

    if server.auth_error:
        raise RuntimeError(server.auth_error)
    if not server.auth_code:
        raise RuntimeError("Authorization code was not received")

    refresh_token = exchange_code_for_refresh_token(server.auth_code)

    print("")
    print("SPOTIFY_REFRESH_TOKEN:")
    print(refresh_token)


if __name__ == "__main__":
    main()
