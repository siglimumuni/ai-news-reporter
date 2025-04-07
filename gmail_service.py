# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachment MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

import os
import pickle
from datetime import datetime
from pytz import timezone

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'mumunisigli@gmail.com'

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

def email_subject():
    hour = datetime.now(tz=timezone('US/Eastern')).hour
    if hour <12:
        return "Morning News Briefing"
    elif hour <=15:
        return "Afternoon News Briefing"
    elif hour <=20:
        return "Evening News Briefing"
    elif hour <=23:
        return "Nightly News Briefing"
    else:
        return "News Briefing"


def create_email(sender, destination, subject, message_text, html_message=None):
    
    #message = MIMEText(body)
    #message['to'] = destination
    #message['from'] = our_email
    #message['subject'] = obj
    #return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    message = MIMEMultipart('alternative') # Use 'alternative' to show either text or HTML
    message['to'] = destination
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, 'plain')
    message.attach(msg)

    if html_message:
        msg = MIMEText(html_message, 'html')
        message.attach(msg)

    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, sender,destination,subject,body,html):
    return service.users().messages().send(userId="me",body=create_email(sender,destination,subject,body,html)
    ).execute()

