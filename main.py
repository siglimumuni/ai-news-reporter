from src.gmail_service import gmail_authenticate,send_email
from src.generate_html import generate_html
from src.news_generation import generate_news_digest
from src.config import GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT
# get the Gmail API service
service = gmail_authenticate()

news_data = generate_news_digest()
print(type(news_data))
print(news_data)

email_body = generate_html(news_data)
print(email_body)


send_email(service, GMAIL_SENDER_EMAIL, RECIPIENT_EMAILS, EMAIL_SUBJECT,email_body)