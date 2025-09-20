import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from utils.gemini import parse_prompt
from utils.helpers import contextualize_prompt # GOTTA ADD INTO CODE
from scheduler import schedule_events
from auth import ensure_auth, get_credentials, get_calendar_service
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta


app = Flask(__name__)

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
app.secret_key = os.getenv("SUPER_SECRET_KEY") 




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    user_prompt = request.form['prompt']
    # gotta add helpers 
    contextual_prompt = contextualize_prompt(user_prompt)
    events = parse_prompt(contextual_prompt)
    service = get_calendar_service()
    if isinstance(events, dict):
        events = [events]

    try:
        return schedule_events(events, service)

    except Exception as e:
        return f"""
            <h3>Error Scheduling Event</h3>
            <p>{str(e)}</p>
            <a href="/">Try Again</a>
        """


        
@app.route('/authorize')
def authorize():
    return ensure_auth()

@app.route('/oauth2callback')
def oauth2callback():
    return get_credentials()


if __name__ == '__main__':
    app.run(debug=True)