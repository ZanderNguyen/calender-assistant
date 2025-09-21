import os
import json
import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import re


load_dotenv()

# Load service account credentials
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())
access_token = credentials.token

# Gemini 2.5 Flash-Lite endpoint
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GEMINI_ENDPOINT = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/gemini-2.5-flash-lite:generateContent"

def call_gemini(prompt: str) -> str:
    """
    Sends a prompt to Gemini and returns the raw text response.
    Used for both event extraction and intent classification.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 512
        }
    }

    response = requests.post(GEMINI_ENDPOINT, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            candidates = response.json().get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from Gemini")

            parts = candidates[0]["content"].get("parts", [])
            if not parts or "text" not in parts[0]:
                raise ValueError("No text part found in Gemini response")

            content = parts[0]["text"]

            # Strip Markdown-style code fencing
            cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip())
            return cleaned

        except Exception as e:
            print("Parsing error:", e)
    else:
        print(f"Gemini API error ({response.status_code}):", response.text)

    return '{"intent": "unknown", "event": {}}'