from flask import redirect, url_for, request, session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CLIENT_SECRETS = "client_secret.json"


def build_flow(state=None):
    return Flow.from_client_secrets_file(
        CLIENT_SECRETS,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True),
    )

def ensure_auth():
    flow = build_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(auth_url)

def get_credentials():
    flow = build_flow(state=session.get("state"))
    flow.fetch_token(code=request.args["code"])
    creds = flow.credentials

    session["credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    return redirect(url_for("index"))

def get_calendar_service():
    creds_data = session.get("credentials")
    if not creds_data:
        return None
    creds = Credentials(**creds_data)
    return build("calendar", "v3", credentials=creds)

