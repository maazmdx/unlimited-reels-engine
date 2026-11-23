#!/usr/bin/env python3
"""
scripts/get_gdrive_oauth_token.py
One-time OAuth authorization flow for Google Drive personal storage.
Generates compact authorized_user JSON for the GDRIVE_CREDENTIALS environment variable.
"""

import sys
import json
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/get_gdrive_oauth_token.py <path_to_client_secret.json>")
        sys.exit(1)

    client_secrets_file = Path(sys.argv[1]).resolve()
    if not client_secrets_file.exists():
        print(f"❌ Error: File not found: {client_secrets_file}")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("❌ Error: google-auth-oauthlib is required.")
        print("Install via: pip install google-auth-oauthlib")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    auth_user = {
        "type": "authorized_user",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri or "https://oauth2.googleapis.com/token",
    }

    compact_json = json.dumps(auth_user, separators=(",", ":"))
    print("\n✅ Compact authorized_user JSON ready for GDRIVE_CREDENTIALS:\n")
    print(compact_json)


if __name__ == "__main__":
    main()
