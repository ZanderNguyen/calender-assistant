import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from utils.gemini import parse_prompt
from flask import redirect, session, url_for
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime


app = Flask(__name__)

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.secret_key = os.getenv("SUPER_SECRET_KEY") 




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    user_prompt = request.form['prompt']
    today = datetime.now().strftime("%A, %d %B %Y")  # e.g., "Friday, 19 September 2025"
    contextual_prompt = f"Today is {today}. {user_prompt}"
    parsed = parse_prompt(contextual_prompt)

    try:
        summary = parsed.get('summary', 'No summary provided')
        start = parsed.get('start_time')
        end = parsed.get('end_time')

        # Check for OAuth credentials
        creds_data = session.get("credentials")
        if not creds_data:
            return redirect(url_for("authorize"))

        creds = Credentials(**creds_data)
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "Pacific/Auckland"},
            "end": {"dateTime": end, "timeZone": "Pacific/Auckland"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()

        return f"""
            <h3>Event Created!</h3>
            <p><strong>Summary:</strong> {summary}</p>
            <p><strong>Start:</strong> {start}</p>
            <p><strong>End:</strong> {end}</p>
            <p><a href="{created_event.get('htmlLink')}" target="_blank">View in Google Calendar</a></p>
            <a href="/">Back</a>
        """

    except Exception as e:
        return f"""
            <h3>Error Scheduling Event</h3>
            <p>{str(e)}</p>
            <a href="/">Try Again</a>
        """


        
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=["https://www.googleapis.com/auth/calendar.events"],
        redirect_uri=url_for("oauth2callback", _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session["state"]
    flow = Flow.from_client_secrets_file(
        "client_secret.json",
        scopes=["https://www.googleapis.com/auth/calendar.events"],
        redirect_uri=url_for("oauth2callback", _external=True),
        state=state
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)