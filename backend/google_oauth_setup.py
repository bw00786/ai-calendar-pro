# google_oauth_setup.py
from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"  # your OAuth client file

    # Load existing token if present
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no valid credentials, do the browser flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"credentials.json not found at {os.path.abspath(creds_path)}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    print("✅ Google Calendar OAuth setup complete. token.json created at:")
    print("   ", os.path.abspath(token_path))

if __name__ == "__main__":
    main()
