from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time


SCOPE = [
    "https://www.googleapis.com/auth/calendar.readonly"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPE_CREDS = CREDS.with_scopes(SCOPE)
CALENDAR_SERVICE = build('calendar', 'v3', credentials=SCOPE_CREDS)


def fetch_events_by_period(
        calendar_id: str,
        start_date: str,
        end_date: str
        ) -> dict:
    """
    Fetches events for a specific calendar 
    within the requested period.
    Returns a list of events.
    Args:
    calendar_id: Google Calendar ID
    start_date: Start date (YYYY-MM-DD)
    end_date: End date (YYYY-MM-DD)
    Returns:
    {"events": [{id, title, start, end}, ...]}
    """
    # Convert string dates to datetime for API
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Expand range to overextended events
    expanded_start = start - timedelta(days=1)

    # Join date + time into datetime for Google Calendar Format compliance
    time_min = datetime.combine(expanded_start, time.min).isoformat() + 'Z'
    time_max = datetime.combine(end, time.max).isoformat() + 'Z'

    # Fetch all events (handle pagination)
    all_events = []
    page_token = None

    while True:
        events_result = CALENDAR_SERVICE.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            pageToken=page_token
        ).execute()

        all_events.extend(events_result.get('items', []))
        page_token = events_result.get('nextPageToken')

        if not page_token:
            break

    # Format events for response
    events = []
    for event in all_events:
        start_info = event.get("start", {})
        end_info = event.get("end", {})

        # Skip all-day events
        if "dateTime" not in start_info:
            continue

        events.append({
            "id": event.get("id"),
            "title": event.get("summary", ""),
            "start": start_info.get("dateTime"),
            "end": end_info.get("dateTime")
        })

    return {"events": events}


# if __name__ == "__main__":
#     result = fetch_events_by_period(
#         "calendar@id",
#         "2025-03-31",
#         "2025-05-31"
#     )
#     total_events = len(result["events"])
#     print(f"Total events: {total_events}")
#     print(result)
