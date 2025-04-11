import os
from dotenv import load_dotenv
from src.gmail_service import email_subject

# Load environment variables from .env file
load_dotenv()

# --- Core Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Specify preferred gemini models
GEMINI_GENERATION_MODEL = "gemini-2.0-flash" #"gemini-2.5-pro-exp-03-25" 
GEMINI_PARSING_MODEL = "gemini-2.0-flash" #"gemini-1.5-flash-latest"

# --- Email Configuration ---
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
# List of recipient emails, comma-separated in the environment variable
RECIPIENT_EMAILS_STR = os.getenv("RECIPIENT_EMAILS")
RECIPIENT_EMAILS = ",".join([email.strip() for email in RECIPIENT_EMAILS_STR.split(',') if email.strip()])

# Email subject based on the time zone
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
EMAIL_SUBJECT = email_subject(TIMEZONE)

# --- HTML Template Configuration ---
# Path to the HTML template file
HTML_TEMPLATE_PATH = "templates/minimalist_professional.html"