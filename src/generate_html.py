import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from src.models import NewsCollection
from src.config import HTML_TEMPLATE_PATH
#from src.exceptions import HtmlGenerationError
#from src.gcp_utils import get_tracer

logger = logging.getLogger(__name__)
#tracer = get_tracer()

# Prepare Jinja2 environment once
try:
    env = Environment(
        loader=FileSystemLoader(searchpath="."), 
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,  # Helps clean up whitespace
        lstrip_blocks=True # Helps clean up whitespace
    )
    logger.info(f"Jinja2 environment initialized, loading templates from filesystem root.")
except Exception as e:
    logger.error(f"Failed to initialize Jinja2 environment: {e}", exc_info=True)
    # Depending on app structure, might want to raise an error here
    env = None # Ensure env is None if setup fails


def generate_html(news_data: NewsCollection) -> str:
    """
    Generates HTML content for the news digest using a Jinja2 template.

    Args:
        news_data: A NewsCollection object containing the news articles.

    Returns:
        A string containing the rendered HTML.

    Raises:
        HtmlGenerationError: If the template cannot be found or rendering fails.
    """
    #if env is None:
        #raise HtmlGenerationError("Jinja2 environment is not initialized.")
        
    #with tracer.start_as_current_span("generate_html_content") as span:
        #logger.info(f"Generating HTML using template: {HTML_TEMPLATE_PATH}")
        #span.set_attribute("html.template_path", HTML_TEMPLATE_PATH)

        #try:
    template = env.get_template(HTML_TEMPLATE_PATH)
            #span.add_event("Template loaded successfully")

            # Render the template with the data
            # Pydantic models can be directly used in Jinja2 context
    html_output = template.render(news_data=news_data)
            #span.add_event("HTML rendering complete")
    logger.info("Successfully generated HTML content for the news digest.")
            #span.set_attribute("html.output_length", len(html_output))
    return html_output

        #except TemplateNotFound:
            #logger.error(f"HTML template not found at path: {HTML_TEMPLATE_PATH}", exc_info=True)
            #span.set_status(trace.Status(trace.StatusCode.ERROR, "TemplateNotFound"))
            #raise HtmlGenerationError(f"Template not found: {HTML_TEMPLATE_PATH}")
        #except Exception as e:
            #logger.error(f"Failed to render HTML template: {e}", exc_info=True)
            #span.set_status(trace.Status(trace.StatusCode.ERROR, f"Template Rendering Error: {type(e).__name__}"))
            #raise HtmlGenerationError(f"Failed to render HTML: {e}") from e