# ruff: noqa: S101
import os.path
from unittest.mock import Mock

from artemis_sg import app_creds


def test_no_valid_credentials(monkeypatch):
    """
    GIVEN no existing app_token
    WHEN app_creds is called
    THEN InstalledAppFlow runs with expected
         credentials filename and scopes
    """
    creds_file = "credentials.json"
    scopes = (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/presentations",
    )

    mock = Mock()
    monkeypatch.setattr(app_creds, "google_credentials", creds_file)
    monkeypatch.setattr(app_creds, "InstalledAppFlow", mock)
    monkeypatch.setattr(app_creds, "_write_token_file", lambda *args, **kwargs: None)

    app_creds.app_creds("bogus")

    mock.from_client_secrets_file.assert_any_call(creds_file, scopes)


def test_valid_credentials(monkeypatch):
    """
    GIVEN a valid app_token
    WHEN app_creds is called
    THEN a credentials object with valid attribute that is set to true
    """
    # Ensure that app_token_filename exists
    monkeypatch.setattr(os.path, "exists", lambda *args: True)
    # Mock `Credentials.from_authorized_user_file` to return
    # a mock_creds mock whose `valid` attribute is True
    mock_creds = Mock(name="mock_creds")
    mock_creds.valid = True
    mock = Mock(return_value=mock_creds)
    monkeypatch.setattr(app_creds.Credentials, "from_authorized_user_file", mock)

    creds = app_creds.app_creds("bogus")

    assert creds.valid is True
