import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachment MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from pydantic import BaseModel #, HttpUrl
from typing import List #, Dict, Optional
import json
import re
from jinja2 import Environment, BaseLoader
import html
from dotenv import load_dotenv
load_dotenv()


from datetime import datetime
from pytz import timezone

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = api_key)
gemini_2_5_pro = "gemini-2.5-pro-exp-03-25"
gemini_2_0_flash = "gemini-2.0-flash"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily News Digest</title>
  <style>
    body {
      font-family: 'Arial', sans-serif;
      margin: 0;
      padding: 0;
      background-color: #f4f4f4;
      color: #333;
      line-height: 1.6;
    }

    .container {
      width: 80%;
      margin: 20px auto;
      background-color: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    }

    h1 {
      color: #2c3e50;
      text-align: center;
      border-bottom: 2px solid #ddd;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }

    h2 {
      color: #3498db; /* Default color, can be overridden by section */
      border-bottom: 1px solid #eee;
      padding-bottom: 5px;
      margin-top: 25px;
    }

    .article {
      margin-bottom: 20px;
    }

    .headline {
      font-size: 1.2em;
      font-weight: bold;
      color: #333;
    }

    .summary {
      margin-top: 5px;
      color: #555;
    }

    .news-provider {
      font-style: italic;
      color: #777;
      margin-top: 5px;
    }

    .source-link {
      display: block;
      margin-top: 5px;
      color: #3498db;
      text-decoration: none;
    }

    .source-link:hover {
      text-decoration: underline;
    }

    /* Category Styles */
    .major-headlines { border-left: 5px solid #3498db; padding-left: 10px; margin-left: 0;}
    .major-headlines h2 { color: #3498db; }
    .key-developments { border-left: 5px solid #9b59b6; padding-left: 10px; margin-left: 0;}
    .key-developments h2 { color: #9b59b6; }
    .conflict { border-left: 5px solid #e74c3c; padding-left: 10px; margin-left: 0;}
    .conflict h2 { color: #e74c3c; }
    .the-global-economy { border-left: 5px solid #f39c12; padding-left: 10px; margin-left: 0;}
    .the-global-economy h2 { color: #f39c12; }
    .business-and-industry { border-left: 5px solid #1abc9c; padding-left: 10px; margin-left: 0;}
    .business-and-industry h2 { color: #1abc9c; }
    .in-canada { border-left: 5px solid #34495e; padding-left: 10px; margin-left: 0;}
    .in-canada h2 { color: #34495e; }
    .science-and-technology { border-left: 5px solid #95a5a6; padding-left: 10px; margin-left: 0;}
    .science-and-technology h2 { color: #95a5a6; }
    .socio-cultural-developments { border-left: 5px solid #d35400; padding-left: 10px; margin-left: 0;}
    .socio-cultural-developments h2 { color: #d35400; }
    .human-interest-stories { border-left: 5px solid #c0392b; padding-left: 10px; margin-left: 0;}
    .human-interest-stories h2 { color: #c0392b; }
    .ai-spotlight { border-left: 5px solid #f1c40f; padding-left: 10px; margin-left: 0;}
    .ai-spotlight h2 { color: #f1c40f; }

    /* Responsive Design */
    @media (max-width: 768px) {
      .container {
        width: 95%;
        padding: 10px;
      }
    }
  </style>
</head>
<body>

  <div class="container">
    <h1>Daily News Digest</h1>

    {% if news_data.majorHeadlines %}
    <section class="major-headlines">
      <h2>Major Headlines</h2>
      {% for article in news_data.majorHeadlines %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.keyDevelopmentsInInternationalAffairs %}
    <section class="key-developments">
      <h2>Key Developments In International Affairs</h2>
      {% for article in news_data.keyDevelopmentsInInternationalAffairs %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.conflict %}
    <section class="conflict">
      <h2>Conflict</h2>
      {% for article in news_data.conflict %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.theGlobalEconomy %}
    <section class="the-global-economy">
      <h2>The Global Economy</h2>
      {% for article in news_data.theGlobalEconomy %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.businessAndIndustry %}
    <section class="business-and-industry">
      <h2>Business and Industry</h2>
      {% for article in news_data.businessAndIndustry %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.inCanada %}
    <section class="in-canada">
      <h2>In Canada</h2>
      {% for article in news_data.inCanada %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.scienceAndTechnology %}
    <section class="science-and-technology">
      <h2>Science and Technology</h2>
      {% for article in news_data.scienceAndTechnology %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.socioCulturalDevelopments %}
    <section class="socio-cultural-developments">
      <h2>Socio-Cultural Developments</h2>
      {% for article in news_data.socioCulturalDevelopments %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.humanInterestStories %}
    <section class="human-interest-stories">
      <h2>Human Interest Stories</h2>
      {% for article in news_data.humanInterestStories %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

    {% if news_data.aiSpotlight %}
    <section class="ai-spotlight">
      <h2>AI Spotlight</h2>
      {% for article in news_data.aiSpotlight %}
      <div class="article">
        <div class="headline">{{ article.headline | escape }}</div>
        <div class="summary">{{ article.summary | escape }}</div>
        <div class="news-provider">{{ article.newsProvider | escape }}</div>
        <a class="source-link" href="{{ article.sourceLink | escape }}">Source</a>
      </div>
      {% endfor %}
    </section>
    {% endif %}

  </div>

</body>
</html>
"""

class Article(BaseModel):
        """A news article."""

        headline: str
        """The headline of the article."""
        summary: str
        """A brief summary of the article."""
        newsProvider: str
        """The name of the news provider."""
        sourceLink: str
        """A link to the original source of the article."""


class NewsCollection(BaseModel):
        """A collection of news articles categorized into different topics."""

        majorHeadlines: List[Article]
        """Major news headlines."""
        keyDevelopmentsInInternationalAffairs: List[Article]
        """Key developments in international affairs."""
        conflict: List[Article]
        """News articles related to conflict."""
        theGlobalEconomy: List[Article]
        """News articles related to the global economy."""
        businessAndIndustry: List[Article]
        """News articles related to business and industry."""
        inCanada: List[Article]
        """News articles specific to Canada."""
        scienceAndTechnology: List[Article]
        """News articles related to science and technology."""
        socioCulturalDevelopments: List[Article]
        """News articles related to socio-cultural developments."""
        humanInterestStories: List[Article]
        """Human interest stories."""
        aiSpotlight: List[Article]
        """News articles related to AI."""


def generate_news(model=gemini_2_5_pro):

    google_search_tool = Tool(
                            google_search = GoogleSearch()
                            )

    response = client.models.generate_content(
                                                model=model,
                                                contents=
                                                """You are a news reporter with over 20 years of experience tracking,
                                                    summarizing and analyzing global news stories. Using the web search tool, Search the web for the latest and
                                                    top global news stories today in the following categories:
                                                    

                                                        1. A brief overview of the major headlines
                                                        2. Key developments in international affairs
                                                        3. Conflict
                                                        4. The Global Economy
                                                        5. Business and Industry
                                                        6. In Canada
                                                        7. Science and Technology
                                                        8. Socio-cultural Developments
                                                        9. Human Interest Stories
                                                        10. AI Spotlight.

                                                    Narrow down to the top 5 stories for each category and provide a 10 word headline, followed by a 50 word 
                                                    summary for each news article in the format  'headline': 'summary'.
                                                    Also include a direct link to the source for each article. 
                                                    You must always return valid JSON fenced by a markdown code block. Do not return any additional text.
                                                    """ ,
                                                    config = GenerateContentConfig(tools = [google_search_tool])
                                                    )
    return response.text


def parse_response(response,model=gemini_2_5_pro):

    parsed_response = client.models.generate_content(
        model=model,
        contents=f"Parse this text: {response} using the supplied schema. Ensure that no news story is duplicated",
        config = GenerateContentConfig(
            response_mime_type="application/json", response_schema=NewsCollection)
        )
    return json.loads(parsed_response.text)


def generate_html(news_data: NewsCollection) -> str:
    """
    Generates HTML for the news digest based on the provided NewsCollection data.

    Args:
        news_data: An instance of NewsCollection containing the news articles.

    Returns:
        A string containing the generated HTML.
    """
    # Set up Jinja2 environment
    # BaseLoader loads templates from strings
    env = Environment(loader=BaseLoader(), autoescape=True) # autoescape=True is default and recommended
    template = env.from_string(HTML_TEMPLATE)

    # Render the template with the data
    # Pydantic models work directly as context variables in Jinja2
    html_output = template.render(news_data=news_data)

    return html_output

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'mumunisigli@gmail.com'

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
service = gmail_authenticate()


def briefing_time():
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

def create_message(sender, destination, obj, message_text, html_message=None):
    
    #message = MIMEText(body)
    #message['to'] = destination
    #message['from'] = our_email
    #message['subject'] = obj
    #return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

    message = MIMEMultipart('alternative') # Use 'alternative' to show either text or HTML
    message['to'] = destination
    message['from'] = sender
    message['subject'] = obj

    msg = MIMEText(message_text, 'plain')
    message.attach(msg)

    if html_message:
        msg = MIMEText(html_message, 'html')
        message.attach(msg)

    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, sender,destination, obj, body,html):
    return service.users().messages().send(userId="me",body=create_message(sender,destination, obj, body,html)
    ).execute()

parsed_response = parse_response(generate_news())
print(parsed_response)
email_body = generate_html(parsed_response)
print(email_body)

send_message(service, "News Reporter Agent <mumunisigli@gmail.com>", "mumunisigli@gmail.com,shellyann.murphy@yahoo.com", briefing_time(), 
            "test", email_body)

#maxwell.edusei@gmail.com
#,shellyann.murphy@yahoo.com,nigel@ianaitch.com


