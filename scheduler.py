from datetime import datetime, timedelta, time
from utils.helpers import is_similar
import json
import pytz

def find_event_by_summary_and_date(service, summary, target_date):
    tz = pytz.timezone("Pacific/Auckland")
    start_dt = tz.localize(datetime.combine(target_date, time.min))
    end_dt = tz.localize(datetime.combine(target_date, time.max))

    print(f"🔍 Searching for '{summary}' between {start_dt.isoformat()} and {end_dt.isoformat()}")

    try:
        events = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            q=summary,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
    except Exception as e:
        print("⚠️ Calendar query failed:", e)
        return None

    print(f"🔍 Found {len(events)} events")

    for event in events:
        print("🔍 Candidate:", event.get("summary"), event.get("start"))
        if is_similar(summary, event.get("summary", "")):
            print("✅ Fuzzy match found")
            return event


    print("⚠️ No exact match found")
    return None


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
    """

def edit_event(event_data, service):
    summary = event_data.get("summary")
    new_start = event_data.get("new_start_time") or event_data.get("start_time")
    new_end = event_data.get("new_end_time") or event_data.get("end_time")
    print("testing")
    # Search for matching event
    target_date = datetime.fromisoformat(new_start).date()
    event = find_event_by_summary_and_date(service, summary, target_date)
    if not event:
        print(f"⚠️ No matching event found for '{summary}' on {target_date}")
        return f"<p>No matching event found for '{summary}' on {target_date}</p>"
    print("Original event:", json.dumps(event, indent=2))
    if not event:
        return f"<p>No matching event found for '{summary}' on {target_date}</p>"

    event_id = event["id"]

    if new_start and not new_end:
        try:
            start_dt = datetime.fromisoformat(new_start)
            new_end = (start_dt + timedelta(hours=1)).isoformat()
        except Exception as e:
            print("⚠️ Failed to parse start_time:", e)
            return "<p>Invalid start time format.</p>"


    if new_start:
        event["start"]["dateTime"] = new_start
        event["start"]["timeZone"] = "Pacific/Auckland"

    if new_end:
        event["end"]["dateTime"] = new_end
        event["end"]["timeZone"] = "Pacific/Auckland"

    try:
        updated = service.events().update(
            calendarId="primary",
            eventId=event_id,
            body=event
        ).execute()

        print("✅ Updated event:", json.dumps(updated, indent=2))

        return f"""
            <h3>✅ Event Updated</h3>
            <p><strong>{updated['summary']}</strong><br>
            {updated['start']['dateTime']} → {updated['end']['dateTime']}<br>
            <a href="{updated.get('htmlLink')}" target="_blank">View in Calendar</a></p>
        """
    except Exception as e:
        print("⚠️ Calendar update failed:", e)
        return f"<p>Failed to update event: {str(e)}"


def delete_event(event_data, service):
    summary = event_data.get("summary")
    start_time = event_data.get("start_time")

    # Fallback to today if start_time is missing
    if not start_time:
        target_date = datetime.now().date()
        print(f"⚠️ No start_time provided for '{summary}', defaulting to today: {target_date}")
    else:
        target_date = datetime.fromisoformat(start_time).date()

    if not summary:
        return "<p>Missing summary for deletion.</p>"

    event = find_event_by_summary_and_date(service, summary, target_date)
    if not event:
        print(f"⚠️ No matching event found for '{summary}' on {target_date}")
        return f"<p>No matching event found for '{summary}' on {target_date}</p>"

    event_id = event["id"]

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        print(f"🗑️ Deleted event: {summary}")
        return f"<h3>🗑️ Event Deleted</h3><p><strong>{summary}</strong> was removed.<br></p>"
    except Exception as e:
        print("⚠️ Failed to delete event:", e)
        return f"<p>Failed to delete event: {str(e)}</p>"