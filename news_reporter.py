import os

# for encoding/decoding messages in base64

from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from pydantic import BaseModel #, HttpUrl
from typing import List #, Dict, Optional
import json
import re
from jinja2 import Environment, BaseLoader
import html
from dotenv import load_dotenv

from gmail_service import gmail_authenticate,send_email,email_subject
load_dotenv()


from datetime import datetime
from pytz import timezone

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key = api_key)
gemini_2_5_pro = "gemini-2.5-pro-exp-03-25"
gemini_2_0_flash = "gemini-2.0-flash"

NEWS_GENERATION_PROMPT = """
You are a highly experienced news editor AI. Your task is to compile a concise and informative news digest covering the most significant global events from the last 12-24 hours.

Use the Google Search tool to find RECENT and RELEVANT news articles for the following categories:
1.  Major Headlines: Top 3-5 most impactful global stories.
2.  Key Developments in International Affairs: Significant diplomatic or political shifts (Top 3-5 stories).
3.  Conflict: Updates on major ongoing conflicts (Top 3-5 stories).
4.  The Global Economy: Important economic news, market trends, policy changes (Top 3-5 stories).
5.  Business and Industry: Major corporate news, sector trends (Top 3-5 stories).
6.  In Canada: Key national news specific to Canada (Top 3-5 stories).
7.  Science and Technology: Breakthroughs, major developments (Top 3-5 stories).
8.  Socio-cultural Developments: Significant societal or cultural trends/events (Top 3-5 stories).
9.  Human Interest Stories: Compelling stories about individuals or communities (Top 2-3 stories).
10. AI Spotlight: Notable advancements or news in Artificial Intelligence (Top 2-3 stories).

For EACH article you include, provide:
- A concise, informative headline (max 15 words).
- A brief summary (around 40-60 words).
- The name of the news provider (e.g., "Reuters", "BBC News", "The Associated Press").
- A direct, working URL (sourceLink) to the original article.

CRITICAL INSTRUCTIONS:
- Focus on the MOST RECENT news (within the last 24 hours preferably).
- Ensure all source links (sourceLink) are valid URLs.
- Do NOT duplicate stories across categories. If a story fits multiple, choose the most relevant one.
- Adhere STRICTLY to the requested JSON output format defined by the schema.
- Do NOT include any introductory text, explanations, or concluding remarks outside the JSON structure.
- If you cannot find sufficient RECENT news for a category, you may return an empty list for that category, but try your best.
"""

# HTML template for the news digest
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
                                                contents=NEWS_GENERATION_PROMPT,
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


# get the Gmail API service
service = gmail_authenticate()




parsed_response = parse_response(generate_news())
print(parsed_response)
email_body = generate_html(parsed_response)
print(email_body)


send_email(service, "News Reporter Agent <mumunisigli@gmail.com>", "mumunisigli@gmail.com",email_subject(),"test",email_body)


