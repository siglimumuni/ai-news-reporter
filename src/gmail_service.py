# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# for encoding the email message
from base64 import urlsafe_b64encode
# for creating the email message
from email.mime.text import MIMEText


import os
import pickle
from datetime import datetime
from pytz import timezone

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
# If modifying these SCOPES, delete the file token.pickle.

def gmail_authenticate():
    credentials = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    # if there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            credentials = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build('gmail', 'v1', credentials=credentials)

# Function to determine the email subject based on the user's timezone
def email_subject(user_timezone):
    hour = datetime.now(tz=timezone(user_timezone)).hour
    if hour >=5 and hour < 12:
        return "Morning News Briefing"
    elif hour >=12 and hour < 16:
        return "Afternoon News Briefing"
    elif hour >=16 and hour < 20:
        return "Evening News Briefing"
    elif hour >=20 and hour < 24:
        return "Nightly News Briefing"
    else:
        return "News Briefing"

# Function to create the email message
def create_email(sender, destination, subject, html_message):
    """_summary_

    Args:
        sender (str):_sender_
        destination (str): _recipient_
        subject (str): _subject_
        html_message (html): _email body_

    Returns:
        html_message (bytes): _encoded email message_
    """
    message = (MIMEText(html_message, 'html'))
    message['to'] = destination
    message['from'] = sender
    message['subject'] = subject

    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

# Function to send the email
def send_email(service, sender,destination,subject,html):
    return service.users().messages().send(userId="me",body=create_email(sender,destination,subject,html)
    ).execute()

