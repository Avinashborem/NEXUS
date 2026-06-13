# skills/calendar_skill.py — Google Calendar Integration
import os, pickle, datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES      = ['https://www.googleapis.com/auth/calendar']
CREDS_FILE  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
CAL_TOKEN   = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'calendar_token.pickle')

def get_service():
    creds = None
    if os.path.exists(CAL_TOKEN):
        with open(CAL_TOKEN, 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(CAL_TOKEN, 'wb') as f:
            pickle.dump(creds, f)
    return build('calendar', 'v3', credentials=creds)

def get_todays_events():
    try:
        service = get_service()
        now     = datetime.datetime.utcnow()
        end     = now.replace(hour=23, minute=59, second=59)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No events scheduled for today, sir."

        summaries = []
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date',''))
            if 'T' in start:
                t = datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
                t = t.astimezone()
                time_str = t.strftime('%I:%M %p')
            else:
                time_str = 'All day'
            summaries.append(f"{e['summary']} at {time_str}")

        return f"Today you have {len(events)} events: " + ", ".join(summaries)
    except Exception as e:
        return f"Could not get calendar: {e}"

def get_upcoming_events(days=7):
    try:
        service = get_service()
        now     = datetime.datetime.utcnow()
        end     = now + datetime.timedelta(days=days)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return f"No events in the next {days} days."

        summaries = []
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date',''))
            if 'T' in start:
                t = datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
                t = t.astimezone()
                date_str = t.strftime('%a %d %b %I:%M %p')
            else:
                date_str = start
            summaries.append(f"{e['summary']} on {date_str}")

        return f"Upcoming events: " + ", ".join(summaries[:5])
    except Exception as e:
        return f"Could not get events: {e}"

def create_event(title, date_str, time_str=None, duration_mins=60, description=""):
    try:
        service = get_service()
        now     = datetime.datetime.now()

        # Parse date
        date_str = date_str.lower().strip()
        if date_str == "today":
            event_date = now.date()
        elif date_str == "tomorrow":
            event_date = (now + datetime.timedelta(days=1)).date()
        else:
            from dateutil import parser as dateparser
            event_date = dateparser.parse(date_str).date()

        # Parse time
        if time_str:
            from dateutil import parser as dateparser
            t = dateparser.parse(time_str)
            start_dt = datetime.datetime.combine(event_date,
                        t.time())
        else:
            start_dt = datetime.datetime.combine(event_date,
                        datetime.time(9, 0))

        end_dt = start_dt + datetime.timedelta(minutes=duration_mins)

        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
        }

        result = service.events().insert(
            calendarId='primary', body=event).execute()
        return f"Event '{title}' created for {start_dt.strftime('%d %b at %I:%M %p')}."
    except ImportError:
        return "Install dateutil: pip install python-dateutil"
    except Exception as e:
        return f"Could not create event: {e}"

def delete_event(title):
    try:
        service = get_service()
        now     = datetime.datetime.utcnow()
        end     = now + datetime.timedelta(days=30)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end.isoformat() + 'Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        for e in events:
            if title.lower() in e['summary'].lower():
                service.events().delete(
                    calendarId='primary',
                    eventId=e['id']).execute()
                return f"Deleted event: {e['summary']}."

        return f"No event found with title: {title}"
    except Exception as e:
        return f"Could not delete event: {e}"

def get_next_event():
    try:
        service = get_service()
        now     = datetime.datetime.utcnow()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            maxResults=1,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return "No upcoming events found."

        e     = events[0]
        start = e['start'].get('dateTime', e['start'].get('date',''))
        if 'T' in start:
            t = datetime.datetime.fromisoformat(start.replace('Z','+00:00'))
            t = t.astimezone()
            time_str = t.strftime('%A %d %B at %I:%M %p')
        else:
            time_str = start

        return f"Next event: {e['summary']} on {time_str}."
    except Exception as e:
        return f"Could not get next event: {e}"