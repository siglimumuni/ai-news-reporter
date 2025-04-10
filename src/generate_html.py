import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.models import NewsCollection
from src.config import HTML_TEMPLATE_PATH

logger = logging.getLogger(__name__)

# Prepare Jinja2 environment
try:
    env = Environment(
        loader=FileSystemLoader(searchpath="."), 
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,  
        lstrip_blocks=True 
    )
    logger.info(f"Jinja2 environment initialized, loading templates from filesystem root.")
except Exception as e:
    logger.error(f"Failed to initialize Jinja2 environment: {e}", exc_info=True)
    
    env = None 


def generate_html(news_data: NewsCollection) -> str:
    """
    Generates HTML content for the news digest using a Jinja2 template.

    Args:
        news_data: A NewsCollection object containing the news articles.

    Returns:
        A string containing the rendered HTML.

    """
    
    template = env.get_template(HTML_TEMPLATE_PATH)
    logger.info(f"Loaded template: {HTML_TEMPLATE_PATH}")

            # Render the template with the data
    html_output = template.render(news_data=news_data)
    logger.info("Successfully generated HTML content for the news digest.")

    return html_output