import os
from dotenv import load_dotenv
from datetime import datetime
from pytz import timezone

# Load environment variables from .env file
load_dotenv()

# Function to determine the email subject based on the user's timezone
def email_subject(user_timezone):
    """
    Determines email subject based on time of day using 24-hour format.
    
    Args:
        user_timezone (str): Timezone string (e.g., 'America/New_York')
    
    Returns:
        str: Appropriate subject line based on time:
            05:00-11:59 -> Morning News
            12:00-15:59 -> Afternoon News
            16:00-19:59 -> Evening News
            20:00-23:59 -> Nightly News
            00:00-04:59 -> News Briefing
    """
    utc = datetime.now(timezone('UTC'))
    now_local = utc.astimezone(timezone(user_timezone))
    
    hour_24 = now_local.hour  # 24-hour format (0-23)
    
    if 5 <= hour_24 < 12:
        x = "Morning News Briefing"
    elif 12 <= hour_24 < 16:
        x = "Afternoon News Briefing"
    elif 16 <= hour_24 < 20:
        x = "Evening News Briefing"
    elif 20 <= hour_24 < 24:
        x = "Nightly News Briefing"
    else:  # 0-4 hours
        x = "Morning News Briefing"
    
    return f"{x} - {now_local.strftime('%a, %b %d %Y - %H:%M %p')}"

# --- Core Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Specify preferred gemini models
GEMINI_GENERATION_MODEL = "gemini-2.0-flash" #"gemini-2.5-pro-exp-03-25" 
GEMINI_PARSING_MODEL = "gemini-2.0-flash" #"gemini-1.5-flash-latest"

# --- Email Configuration ---
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
# List of recipient emails, comma-separated in the environment variable
RECIPIENT_EMAILS_STR = os.getenv("RECIPIENT_EMAIL_LIST")
RECIPIENT_EMAILS = ",".join([email.strip() for email in RECIPIENT_EMAILS_STR.split(',') if email.strip()])

# Email subject based on the time zone
TIMEZONE = os.getenv("TIMEZONE","UTC")  # Default to UTC if not set
EMAIL_SUBJECT = email_subject(TIMEZONE)

# --- HTML Template Configuration ---
# Path to the HTML template file
HTML_TEMPLATE_PATH = "templates/minimalist_professional.html"