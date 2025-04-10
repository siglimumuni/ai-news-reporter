from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# --- Models ---
# Define the models for the news articles and collections
# These models are used to structure the data received from the Gemini API and to validate it.
class Article(BaseModel):
    """Represents a single news article."""
    headline: str = Field(..., description="The headline of the article.")
    summary: str = Field(..., description="A brief summary of the article.")
    news_provider: Optional[str] = Field(None, alias="newsProvider", description="The name of the news provider.") # Allow None if model omits
    source_link: Optional[str] = Field(None, alias="sourceLink", description="A valid link to the original source.") 

    # Pydantic v2 style validator
    @field_validator('source_link', mode='before')
    def check_source_link(cls, v):
        if isinstance(v, str) and not v.startswith(('http://', 'https://')):
            logger.warning(f"Correcting invalid source link format: {v}")
            return None 
        # Handle cases where the LLM might return an empty string or non-URL value
        if not v:
            logger.warning("Received empty source link.")
            return None
        return v

    class Config:
        validate_by_name = True 

# Define the collection of articles
# This model is used to group articles into different categories for the news digest.
class NewsCollection(BaseModel):
    """A collection of news articles categorized into different topics."""
    # Each field represents a category of news articles
    major_headlines: List[Article] = Field(default_factory=list, alias="majorHeadlines")
    key_developments_international: List[Article] = Field(default_factory=list, alias="keyDevelopmentsInInternationalAffairs")
    conflict_news: List[Article] = Field(default_factory=list, alias="conflict")
    global_economy_news: List[Article] = Field(default_factory=list, alias="theGlobalEconomy")
    business_industry_news: List[Article] = Field(default_factory=list, alias="businessAndIndustry")
    canada_news: List[Article] = Field(default_factory=list, alias="inCanada")
    science_tech_news: List[Article] = Field(default_factory=list, alias="scienceAndTechnology")
    socio_cultural_news: List[Article] = Field(default_factory=list, alias="socioCulturalDevelopments")
    human_interest_stories: List[Article] = Field(default_factory=list, alias="humanInterestStories")
    ai_spotlight_news: List[Article] = Field(default_factory=list, alias="aiSpotlight")

    class Config:
        validate_by_name = True
