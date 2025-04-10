import logging
import json
from google.genai import Client as GeminiClient
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch # Corrected import
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions as google_api_exceptions # Import Google API exceptions

from src.config import GEMINI_API_KEY, GEMINI_GENERATION_MODEL, GEMINI_PARSING_MODEL
from src.models import NewsCollection


logger = logging.getLogger(__name__)

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
- Do NOT include any introductory text, explanations, or concluding remarks outside the JSON structure.
- If you cannot find sufficient RECENT news for a category, you may return an empty list for that category, but try your best.
"""

# Configure retry mechanism for Gemini API calls
# Retry on specific Google API transient errors and potentially others
retry_decorator = retry(
    stop=stop_after_attempt(3), # Retry 3 times
    wait=wait_exponential(multiplier=1, min=4, max=10), # Exponential backoff (4s, 8s)
    retry=(
            retry_if_exception_type(google_api_exceptions.ServiceUnavailable) |
            retry_if_exception_type(google_api_exceptions.ResourceExhausted) |
            retry_if_exception_type(google_api_exceptions.DeadlineExceeded)
            ),
    before_sleep=lambda retry_state: logger.warning(f"Retrying Gemini API call after error: {retry_state.outcome.exception()} (Attempt {retry_state.attempt_number})")
)

@retry_decorator
def generate_news_digest() -> NewsCollection:
    """
    Generates a news digest using the Gemini API with Google Search tool,
    requesting structured JSON output directly based on the NewsCollection schema.

    Returns:
        NewsCollection: A Pydantic model instance containing the categorized news.

    """
    
    logger.info(f"Initiating news generation using model: {GEMINI_GENERATION_MODEL}")

    # Initialize the Gemini client
    client = GeminiClient(api_key=GEMINI_API_KEY)

    # Define the Google Search tool
    google_search_tool = Tool(google_search=GoogleSearch()) # Simplified usage

    # Configure generation settings
    # Requesting JSON output directly via response_mime_type and response_schema
    generation_config = GenerateContentConfig(
            tools=[google_search_tool],
            )

            
    # Use the client instance's generate_content method
    response = client.models.generate_content(
                model=GEMINI_GENERATION_MODEL, 
                contents=NEWS_GENERATION_PROMPT,
                config=generation_config,
            )
            

    # Parse the response using the NewsCollection schema
    parsed_response = client.models.generate_content(
        model=GEMINI_PARSING_MODEL,
        contents=f"""Parse this text: {response.text} using the supplied schema. Do NOT duplicate stories across categories. 
        If a story fits multiple, choose the most relevant one.Adhere STRICTLY to the requested JSON output format defined by the schema.
        Do NOT include any introductory text, explanations, or concluding remarks outside the JSON structure.""",
        config = GenerateContentConfig(
            response_mime_type="application/json", response_schema=NewsCollection)
        )
    news_data = json.loads(parsed_response.text)


    return news_data
