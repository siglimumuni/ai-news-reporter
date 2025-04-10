import os
import logging
from dotenv import load_dotenv
from src.gmail_service import email_subject

# Load environment variables from .env file for local development
# In GCP Cloud Functions, set these environment variables directly
load_dotenv()

logger = logging.getLogger(__name__)

# --- Core Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set.")
    

# Specify preferred models (could be made configurable)
GEMINI_GENERATION_MODEL = "gemini-2.0-flash" #"gemini-2.5-pro-exp-03-25" # # 
#GEMINI_PARSING_MODEL = "gemini-1.5-flash-latest" # Or use the same model if efficient

# --- Email Configuration ---
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")
# List of recipient emails, comma-separated in the environment variable
RECIPIENT_EMAILS_STR = os.getenv("RECIPIENT_EMAILS")
RECIPIENT_EMAILS = ",".join([email.strip() for email in RECIPIENT_EMAILS_STR.split(',') if email.strip()])

TIMEZONE = os.getenv("TIMEZONE", "America/New_York") # Default timezone


EMAIL_SUBJECT = email_subject(TIMEZONE)

if not RECIPIENT_EMAILS:
    logger.warning("RECIPIENT_EMAILS environment variable not set or empty.")


# Gmail API Scopes
GMAIL_SCOPES = ['https://mail.google.com/']

# --- Application Settings ---

HTML_TEMPLATE_PATH = "templates/minimalist_professional.html"

# --- Observability ---#
# Set to true via env var to enable detailed tracing (can add overhead)
#ENABLE_TRACING = os.getenv("ENABLE_TRACING", "false").lower() == "true"
#GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") # Often set automatically in GCP env

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

TIMEZONE = os.getenv("TIMEZONE", "America/New_York") # Default timezone


# --- Validation (Optional but recommended) ---
# def validate_config():
#     """Basic check to ensure critical variables are present."""
#     critical_vars = {
#         "GEMINI_API_KEY": GEMINI_API_KEY,
#         "GMAIL_SENDER_EMAIL": GMAIL_SENDER_EMAIL,
#         "RECIPIENT_EMAILS": RECIPIENT_EMAILS,
#         # Add check for GCP_SERVICE_ACCOUNT_FILE only if ADC is not expected
#     }
#     missing = [name for name, value in critical_vars.items() if not value]
#     if missing:
#         raise ValueError(f"Missing critical configuration variables: {', '.join(missing)}")
#     logger.info("Configuration loaded successfully.")

# validate_config() # Call validation on import if desired