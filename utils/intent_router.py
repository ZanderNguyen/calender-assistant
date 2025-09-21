import json
from utils.gemini import call_gemini

def parse_intent_and_event(prompt: str):
    full_prompt = (
        "You are a calendar assistant. Based on the user's input, return a single JSON array. "
        "Each item should be an object with two keys:\n"
        "- 'intent': one of 'schedule', 'edit', or 'delete'\n"
        "- 'event': a dictionary with relevant fields like summary, start_time, end_time, etc.\n"
        "Use ISO 8601 format. Do not include any explanation or extra text."
        f"\nUser input: {prompt}"
    )

    raw = call_gemini(full_prompt)
    print("🔍 Raw Gemini response:", raw)

    try:
        parsed_list = json.loads(raw)
        return parsed_list  # List of dicts
    except Exception as e:
        print("⚠️ Failed to parse Gemini response:", e)
        return []