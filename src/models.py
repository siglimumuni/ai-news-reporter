from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class Article(BaseModel):
    """Represents a single news article."""
    headline: str = Field(..., description="The headline of the article.")
    summary: str = Field(..., description="A brief summary of the article.")
    news_provider: Optional[str] = Field(None, alias="newsProvider", description="The name of the news provider.") # Allow None if model omits
    source_link: Optional[str] = Field(None, alias="sourceLink", description="A valid link to the original source.") # Use HttpUrl for validation

    # Pydantic v2 style validator
    @field_validator('source_link', mode='before')
    def check_source_link(cls, v):
        if isinstance(v, str) and not v.startswith(('http://', 'https://')):
            logger.warning(f"Correcting invalid source link format: {v}")
            return None # Or attempt correction if possible, otherwise reject
        # Handle cases where the LLM might return an empty string or non-URL value
        if not v:
            logger.warning("Received empty source link.")
            return None
        return v

    class Config:
        validate_by_name = True # Allows using 'newsProvider' and 'sourceLink' in input data


class NewsCollection(BaseModel):
    """A collection of news articles categorized into different topics."""
    # Use Field with alias for consistency with original JSON expectation if needed,
    # but pythonic names are preferred internally. Pydantic handles mapping.
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

    # Optional: Add a method to check for empty collection
    def is_empty(self) -> bool:
        """Checks if any news articles were collected."""
        all_lists = [
            self.major_headlines, self.key_developments_international, self.conflict_news,
            self.global_economy_news, self.business_industry_news, self.canada_news,
            self.science_tech_news, self.socio_cultural_news, self.human_interest_stories,
            self.ai_spotlight_news
        ]
        return not any(all_lists) # True if all lists are empty