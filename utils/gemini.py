from datetime import datetime, timedelta

def parse_prompt(prompt):
    # This is a placeholder for Gemini Flash-Lite
    # Replace with actual API call later
    now = datetime.utcnow()
    return {
        'summary': prompt,
        'start_time': (now + timedelta(hours=1)).isoformat() + 'Z',
        'end_time': (now + timedelta(hours=2)).isoformat() + 'Z'
    }