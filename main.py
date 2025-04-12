import logging
from flask import Flask, jsonify 
from src.gmail_service import gmail_authenticate, send_email
from src.generate_html import generate_html
from src.news_generation import generate_news_digest
from src.config import GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT

# Configure basic logging - Cloud Run automatically captures stdout/stderr
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route('/send-news')
def send_news():
    """Endpoint to send news digest via email."""
    logging.info("Received request for /send-news")
    try:
        # get the Gmail API service
        logging.info("Authenticating Gmail service...")
        service = gmail_authenticate()
        logging.info("Gmail service authenticated.")

        logging.info("Generating news digest...")
        news_data = generate_news_digest()
        logging.info(f"Generated news data for {len(news_data)} items.") # Example log

        logging.info("Generating HTML body...")
        email_body = generate_html(news_data)
        logging.info("HTML body generated.")

        logging.info(f"Sending email to: {RECIPIENT_EMAILS}")
        send_email(service, GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT, email_body)
        logging.info("Email sent successfully.")


        return jsonify({"status": "success", "message": "News digest sent successfully!"}), 200

    except Exception as e:
        # Log the full error traceback for debugging in Cloud Run Logs
        logging.error(f"An error occurred in /send-news: {e}", exc_info=True)

        # Return an error response to the client
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)