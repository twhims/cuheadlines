import os
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# College URL mapping - Direct newsroom URLs
COLLEGE_URLS = {
    "College of Agriculture, Forestry and Life Sciences": "https://news.clemson.edu/section/college-of-agriculture-forestry-and-life-sciences/",
    "College of Architecture, Art and Construction": "https://news.clemson.edu/section/college-of-architecture-art-and-construction/",
    "College of Arts and Humanities": "https://news.clemson.edu/section/college-of-arts-and-humanities/",
    "College of Behavioral, Social and Health Sciences": "https://news.clemson.edu/section/college-of-behavioral-social-and-health-sciences/",
    "College of Education": "https://news.clemson.edu/section/college-of-education/",
    "College of Engineering, Computing and Applied Sciences": "https://news.clemson.edu/section/college-of-engineering-computing-and-applied-sciences/",
    "College of Science": "https://news.clemson.edu/section/college-of-science/",
    "Harvey S. Peeler Jr. College of Veterinary Medicine": "https://news.clemson.edu/section/college-of-veterinary-medicine/",
    "Wilbur O. and Ann Powers College of Business": "https://news.clemson.edu/section/wilbur-o-and-ann-powers-college-of-business/"
}


def get_college_url(college_name: str) -> str:
    """
    Get the URL for a college news website
    
    Args:
        college_name: The name of the college
    
    Returns:
        The URL for the college news website
    
    Raises:
        ValueError: If the college name is not found
    """
    if college_name in COLLEGE_URLS:
        news_url = COLLEGE_URLS[college_name]
        logger.info(f"Returning direct newsroom URL: {news_url}")
        return news_url
    
    raise ValueError(f"College name not found: {college_name}")


def format_output(college_name: str, articles: List[Dict[str, Any]]) -> str:
    """
    Format the output for the API response
    
    Args:
        college_name: The name of the college
        articles: A list of article dictionaries
    
    Returns:
        A formatted string containing the news summaries
    """
    if not articles:
        return f"No recent news articles found for {college_name}."
    
    # Format the output as a structured text
    output = [f"# Latest News from {college_name}"]
    
    for i, article in enumerate(articles, 1):
        headline = article.get('rewritten_headline', article.get('headline', 'Untitled Article'))
        summary = article.get('summary', 'No summary available.')
        url = article.get('url', '#')
        
        # Add sentiment if available
        sentiment_info = ""
        if 'sentiment' in article:
            sentiment = article['sentiment']
            rating = sentiment.get('rating', 0)
            stars = "★" * rating + "☆" * (5 - rating)
            confidence = sentiment.get('confidence', 0)
            explanation = sentiment.get('explanation', '')
            sentiment_info = f"\nTone: {stars} ({explanation})"
        
        # Format each article
        output.append(f"## {i}. {headline}")
        output.append(f"{summary}{sentiment_info}")
        output.append(f"[Read full article]({url})\n")
    
    return "\n".join(output)


def get_host_url() -> str:
    """
    Get the host URL from environment variables
    
    Returns:
        The host URL
    """
    host = os.environ.get("HOST")
    if not host:
        # Default to a localhost URL for development
        host = "http://localhost:5000"
    
    return host
