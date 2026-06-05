# skills/email_skill.py — Gmail Integration
import os, base64, pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

CREDS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
TOKEN_FILE  = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'token.pickle')

def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Temporarily bring browser to front
            import subprocess
            flow  = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
    return build('gmail', 'v1', credentials=creds)


def read_emails(count=5, unread_only=True):
    try:
        service  = get_service()
        query    = "is:unread" if unread_only else ""
        results  = service.users().messages().list(
            userId='me', q=query, maxResults=count).execute()
        messages = results.get('messages', [])

        if not messages:
            return "No unread emails, sir."

        summaries = []
        for msg in messages[:count]:
            data    = service.users().messages().get(
                userId='me', id=msg['id'], format='metadata',
                metadataHeaders=['From','Subject','Date']).execute()
            headers = {h['name']: h['value']
                       for h in data['payload']['headers']}
            sender  = headers.get('From','Unknown')
            subject = headers.get('Subject','No subject')
            # Clean sender name
            if '<' in sender:
                sender = sender.split('<')[0].strip().strip('"')
            summaries.append(f"From {sender}: {subject}")

        return f"You have {len(messages)} unread emails. " + ". ".join(summaries[:3])

    except Exception as e:
        return f"Couldn't read emails: {e}"


def send_email(to, subject, body):
    try:
        service = get_service()
        msg     = MIMEMultipart()
        msg['To']      = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(
            userId='me', body={'raw': raw}).execute()
        return f"Email sent to {to} successfully, sir."
    except Exception as e:
        return f"Couldn't send email: {e}"


def get_email_body(index=0, unread_only=True):
    """Read the full body of a specific email"""
    try:
        service  = get_service()
        query    = "is:unread" if unread_only else ""
        results  = service.users().messages().list(
            userId='me', q=query, maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages or index >= len(messages):
            return "No email found at that position."

        data    = service.users().messages().get(
            userId='me', id=messages[index]['id'],
            format='full').execute()
        headers = {h['name']: h['value']
                   for h in data['payload']['headers']}
        sender  = headers.get('From','Unknown')
        subject = headers.get('Subject','No subject')

        # Extract body
        body = ""
        payload = data['payload']
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(
                        part['body']['data']).decode('utf-8', errors='ignore')
                    break
        elif 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8', errors='ignore')

        body = body[:500].strip()
        return f"Email from {sender}. Subject: {subject}. Message: {body}"

    except Exception as e:
        return f"Couldn't read email body: {e}"


def mark_as_read(index=0):
    try:
        service  = get_service()
        results  = service.users().messages().list(
            userId='me', q="is:unread", maxResults=10).execute()
        messages = results.get('messages', [])
        if not messages or index >= len(messages):
            return "No unread email found."
        service.users().messages().modify(
            userId='me', id=messages[index]['id'],
            body={'removeLabelIds': ['UNREAD']}).execute()
        return "Marked as read, sir."
    except Exception as e:
        return f"Couldn't mark as read: {e}"