"""artemis_sg.app_creds

Obtains Google API Application Credentials."""

import os.path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from artemis_sg.config import CFG

app_token = CFG["google"]["docs"]["api_creds_token"]
google_credentials = CFG["google"]["docs"]["api_creds_file"]


def app_creds(app_token_filename: str = app_token) -> str:
    """Obtain Google API application credentials.

    Check given `app_token_filename` for valid credentials.  If they don't
    exist or are not valid, then use
    `google_auth_oauthlib.flow.InstalledAppFlow` to let the user manually
    approve the credential request.  When successful, the credentials are saved
    to the given `app_token_filename` and returned.

    :param app_token_filename:
        The filename used to inspect and save the credentials in (default is
        app_creds_token.json).  In practice this would not be set, but is given
        here as a parameter for unittesting purposes.
    :returns: a json string of the credentials
    """

    scopes = (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/presentations",
    )
    creds = None
    # The file `app_token_filename` stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    if os.path.exists(app_token_filename):
        creds = Credentials.from_authorized_user_file(app_token_filename, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                flow = InstalledAppFlow.from_client_secrets_file(
                    google_credentials, scopes
                )
                creds = flow.run_local_server(port=0)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(google_credentials, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        _write_token_file(app_token_filename, creds)

    return creds


def _write_token_file(filename: str, creds: str):
    with open(filename, "w", encoding="utf-8") as token:
        token.write(creds.to_json())
