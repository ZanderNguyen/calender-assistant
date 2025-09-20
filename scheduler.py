from datetime import datetime, timedelta

def schedule_events(events, service):
    results = []

    for event_data in events:
        summary = event_data.get('summary', 'No summary provided')
        start = event_data.get('start_time') or datetime.now().replace(second=0, microsecond=0).isoformat()
        end = event_data.get('end_time') or (datetime.fromisoformat(start) + timedelta(hours=1)).isoformat()

        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "Pacific/Auckland"},
            "end": {"dateTime": end, "timeZone": "Pacific/Auckland"},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        results.append(f"""
            <p><strong>{summary}</strong><br>
            {start} → {end}<br>
            <a href="{created_event.get('htmlLink')}" target="_blank">View in Calendar</a></p>
        """)

    return f"""
        <h3>Events Created!</h3>
        {''.join(results)}
        <a href="/">Back</a>
    """