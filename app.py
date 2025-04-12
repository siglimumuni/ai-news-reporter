from src.gmail_service import gmail_authenticate,send_email
from src.generate_html import generate_html
from src.news_generation import generate_news_digest
from src.config import GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT
from flask import Flask


app = Flask(__name__)
# get the Gmail API service
service = gmail_authenticate()

news_data = generate_news_digest()

email_body = generate_html(news_data)


send_email(service, GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT,email_body)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
    
