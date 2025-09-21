import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
from utils.gemini import call_gemini
from utils.helpers import contextualize_prompt
from utils.intent_router import parse_intent_and_event
from scheduler import schedule_events, edit_event, delete_event
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

app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clear', methods=['POST'])
def clear_history():
    session["history"] = []
    return render_template("index.html", response="<p>🧹 History cleared.</p>", history=[])


@app.route('/action', methods=['POST'])
def handle_action():
    user_prompt = request.form['prompt']
    contextual_prompt = contextualize_prompt(user_prompt)

    parsed_list = parse_intent_and_event(contextual_prompt)
    service = get_calendar_service()
    if not service:
        return redirect(url_for("authorize"))

    responses = []

    try:
        for parsed in parsed_list:
            intent = parsed.get("intent")
            event_data = parsed.get("event")

            if intent == "schedule":
                responses.append(schedule_events([event_data], service))
            elif intent == "edit":
                if not event_data.get("summary") or not (event_data.get("new_start_time") or event_data.get("start_time")):
                    responses.append("<p>✏️ Edit request missing summary or new time. Try rephrasing.</p>")
                else:
                    responses.append(edit_event(event_data, service))

            elif intent == "delete":
                if not event_data.get("summary"):
                    responses.append("<p>🗑️ Delete request missing event summary. Try rephrasing.</p>")
                else:
                    responses.append(delete_event(event_data, service))

            else:
                responses.append("<p>🤔 Unknown intent.</p>")

        html_response = "".join(responses)

        # Store in session history
        if "history" not in session:
            session["history"] = []

        session["history"].append(f"<strong>{user_prompt}</strong><br>{html_response}")

        return render_template("index.html", response="html_response", history=session["history"])

    except Exception as e:
        return render_template("index.html", response=f"""
            <h3>⚠️ Something went wrong</h3>
            <p>{str(e)}</p>
            <a href="/">Try Again</a>
        """, history=session.get("history", []))
        
@app.route('/authorize')
def authorize():
    return ensure_auth()

@app.route('/oauth2callback')
def oauth2callback():
    return get_credentials()

if __name__ == '__main__':
    app.run(debug=True)