import os
import logging
from dotenv import load_dotenv
from src.gmail_service import email_subject

# Load environment variables from .env file
load_dotenv()

# --- Logging Configuration ---
logger = logging.getLogger(__name__)

# --- Core Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set.")
    

# Specify preferred gemini models
GEMINI_GENERATION_MODEL = "gemini-2.0-flash" #"gemini-2.5-pro-exp-03-25" 
GEMINI_PARSING_MODEL = "gemini-2.0-flash" #"gemini-1.5-flash-latest"

# --- Email Configuration ---
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
# List of recipient emails, comma-separated in the environment variable
RECIPIENT_EMAILS_STR = os.getenv("RECIPIENT_EMAILS")
RECIPIENT_EMAILS = ",".join([email.strip() for email in RECIPIENT_EMAILS_STR.split(',') if email.strip()])

if not RECIPIENT_EMAILS:
    logger.warning("RECIPIENT_EMAILS environment variable not set or empty.")
    
# Email subject based on the time zone
TIMEZONE = os.getenv("TIMEZONE", "America/New_York")
EMAIL_SUBJECT = email_subject(TIMEZONE)

# --- HTML Template Configuration ---
# Path to the HTML template file
HTML_TEMPLATE_PATH = "templates/minimalist_professional.html"

if not os.path.exists(HTML_TEMPLATE_PATH):
    logger.warning(f"HTML_TEMPLATE_PATH does not exist: {HTML_TEMPLATE_PATH}")

# --- Logging ---   
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# --- Validation ---
def validate_config():
    """Basic check to ensure critical variables are present."""
    critical_vars = {
        "GEMINI_API_KEY": GEMINI_API_KEY,
        "GMAIL_SENDER_EMAIL": GMAIL_SENDER_EMAIL,
        "RECIPIENT_EMAILS": RECIPIENT_EMAILS,
        "HTML_TEMPLATE_PATH": HTML_TEMPLATE_PATH}
    missing = [name for name, value in critical_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing critical configuration variables: {', '.join(missing)}")
    logger.info("Configuration loaded successfully.")

validate_config()