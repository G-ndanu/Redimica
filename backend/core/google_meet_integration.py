import os
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta


# Define the scope for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Set the path to credentials and token
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Gets /backend/core/
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials', 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'credentials', 'token.json')


def get_credentials():
    creds = None

    # Check if token.json exists
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid credentials, go through authentication flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh token if expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            flow.redirect_uri = "http://127.0.0.1:8000/api/auth/callback/google"  # Ensure this matches Google Console
            creds = flow.run_local_server(port=8000)

        # Save the new credentials
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

from datetime import datetime, timedelta

def create_google_meet_link(scheduled_date, scheduled_time):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # Ensure correct datetime format (handle HH:MM or HH:MM:SS)
    try:
        start_time = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        start_time = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")

    end_time = start_time + timedelta(minutes=30)

    event = {
        'summary': 'Virtual Consultation',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Africa/Nairobi'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Africa/Nairobi'},
        'conferenceData': {
            'createRequest': {
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                'requestId': str(int(datetime.now().timestamp()))  # Unique request ID
            }
        }
    }

    event_result = service.events().insert(
        calendarId='primary',
        body=event,
        conferenceDataVersion=1
    ).execute()

    return event_result.get('hangoutLink', '')



# Test authentication when running directly
if __name__ == "__main__":
    creds = get_credentials()
    print("Authentication successful! Token.json generated.")
