import logging
import json
from google.genai import Client as GeminiClient
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch # Corrected import
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions as google_api_exceptions # Import Google API exceptions

from src.config import GEMINI_API_KEY, GEMINI_GENERATION_MODEL
from src.models import NewsCollection
#from src.exceptions import NewsGenerationError, NewsParsingError, ConfigurationError
#from src.gcp_utils import get_tracer

logger = logging.getLogger(__name__)
#tracer = get_tracer()

# --- Improved Prompt ---
# Store the prompt separately for maintainability
# Use f-string later if dynamic elements like date/time are needed
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

    Raises:
        ConfigurationError: If the API key is missing.
        NewsGenerationError: If the Gemini API call fails after retries.
        NewsParsingError: If the response from Gemini is not valid JSON or doesn't match the schema.
    """
    # if not GEMINI_API_KEY:
    #     raise ConfigurationError("GEMINI_API_KEY is not configured.")

    #with tracer.start_as_current_span("generate_news_digest") as span:
    logger.info(f"Initiating news generation using model: {GEMINI_GENERATION_MODEL}")
        #span.set_attribute("gemini.model", GEMINI_GENERATION_MODEL)

    #try:
            # Initialize Gemini Client
            # Consider client reuse if this function is called frequently in the same process
    client = GeminiClient(api_key=GEMINI_API_KEY)

            # Define the Google Search tool
    google_search_tool = Tool(google_search=GoogleSearch()) # Simplified usage

            # Configure generation settings
            # Requesting JSON output directly via response_mime_type and response_schema
    generation_config = GenerateContentConfig(
            #response_mime_type="application/json",
            #response_schema=NewsCollection.model_json_schema(), # Provide the Pydantic schema
            tools=[google_search_tool],
                # Add temperature, top_k, top_p etc. if needed for creativity/predictability control
                # temperature=0.7
            )

            #span.add_event("Calling Gemini API")
            # Use the client instance's generate_content method
    response = client.models.generate_content(
                model=GEMINI_GENERATION_MODEL, # Ensure you're using a model supporting JSON mode & tools
                contents=NEWS_GENERATION_PROMPT,
                config=generation_config,
            )
            #span.add_event("Received response from Gemini API")

            # Log raw response for debugging if needed (be mindful of PII/data size)
            # logger.debug(f"Raw Gemini Response Text: {response.text}") # Use .text for direct JSON string

            # Check if response content exists
        #if not response.candidates or not response.candidates[0].content.parts:
                #logger.error("Gemini response is empty or missing content parts.")
                #span.set_status(trace.Status(trace.StatusCode.ERROR, "Empty Gemini response"))
                    #raise NewsGenerationError("Received empty response from Gemini API.")


            # --- Parsing and Validation ---
            # Since we requested JSON directly, response.text should be the JSON string
            #try:
                #with tracer.start_as_current_span("parse_gemini_response") as parse_span:
                    # The response.text *should* be valid JSON matching the schema
                    # Pydantic will raise ValidationError if it doesn't match
    #news_data = NewsCollection.model_validate_json(response.text)
                    #logger.info(f"Successfully parsed Gemini response into NewsCollection model.")
                    #parse_span.set_attribute("parsing.successful", True)
                    # Optional: Log counts per category
                    # for category, articles in news_data.dict().items():
                    #     if isinstance(articles, list):
                    #         logger.debug(f"Category '{category}': {len(articles)} articles")

                # --- Post-Parsing Deduplication (Optional - Prompt tries to handle this) ---
                # If needed, implement deduplication logic here based on headline/sourceLink
                # logger.info("Starting post-parsing deduplication...")
                # ... deduplication logic ...
                # logger.info("Deduplication complete.")


                #if news_data.is_empty():
                    #logger.warning("News generation resulted in an empty collection.")
                    #span.set_attribute("news.collection_empty", True)
                #else:
                    #span.set_attribute("news.total_articles", sum(len(getattr(news_data, field)) for field in news_data.__fields__))
    parsed_response = client.models.generate_content(
        model=GEMINI_GENERATION_MODEL,
        contents=f"""Parse this text: {response.text} using the supplied schema. Do NOT duplicate stories across categories. 
        If a story fits multiple, choose the most relevant one.Adhere STRICTLY to the requested JSON output format defined by the schema.
        Do NOT include any introductory text, explanations, or concluding remarks outside the JSON structure.""",
        config = GenerateContentConfig(
            response_mime_type="application/json", response_schema=NewsCollection)
        )
    news_data = json.loads(parsed_response.text)


    return news_data

            #except json.JSONDecodeError as e:
                # logger.error(f"Failed to decode JSON from Gemini response: {e}", exc_info=True)
                # logger.error(f"Invalid JSON received: {response.text[:500]}...") # Log beginning of bad response
            #     span.set_status(trace.Status(trace.StatusCode.ERROR, "JSONDecodeError"))
            #     parse_span.set_status(trace.Status(trace.StatusCode.ERROR, "JSONDecodeError"))
            #     raise NewsParsingError(f"Gemini response was not valid JSON: {e}") from e
            # #except Exception as e: # Catch Pydantic's ValidationError or other parsing issues
            #     logger.error(f"Failed to parse Gemini JSON response into NewsCollection: {e}", exc_info=True)
            #     logger.error(f"JSON content causing error: {response.text[:500]}...")
            #     span.set_status(trace.Status(trace.StatusCode.ERROR, "Pydantic Validation Error or other parsing error"))
            #     parse_span.set_status(trace.Status(trace.StatusCode.ERROR, "Pydantic Validation Error or other parsing error"))
            #     raise NewsParsingError(f"Failed to validate Gemini response against schema: {e}") from e

        # Handle specific API errors after retries fail
        # except google_api_exceptions.GoogleAPIError as e:
        #      logger.error(f"Gemini API call failed after retries: {e}", exc_info=True)
        #      span.set_status(trace.Status(trace.StatusCode.ERROR, f"Gemini API Error: {type(e).__name__}"))
        #      raise NewsGenerationError(f"Gemini API error after retries: {e}") from e
        # # Handle potential errors from the Gemini library itself
        # except Exception as e:
        #     logger.error(f"An unexpected error occurred during news generation: {e}", exc_info=True)
        #     span.set_status(trace.Status(trace.StatusCode.ERROR, f"Unexpected Error: {type(e).__name__}"))
        #     raise NewsGenerationError(f"An unexpected error occurred: {e}") from e
