import os
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# College URL mapping
COLLEGE_URLS = {
    "College of Agriculture, Forestry and Life Sciences": "https://www.clemson.edu/cafls",
    "College of Architecture, Art and Construction": "https://www.clemson.edu/caah",
    "College of Arts and Humanities": "https://www.clemson.edu/caah",
    "College of Behavioral, Social and Health Sciences": "https://www.clemson.edu/cbshs",
    "College of Education": "https://www.clemson.edu/education",
    "College of Engineering, Computing and Applied Sciences": "https://www.clemson.edu/cecas",
    "College of Science": "https://www.clemson.edu/science",
    "Harvey S. Peeler Jr. College of Veterinary Medicine": "https://www.clemson.edu/cafls/veterinary-medicine",
    "Wilbur O. and Ann Powers College of Business": "https://www.clemson.edu/business"
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
        base_url = COLLEGE_URLS[college_name]
        # Try to append a typical news path
        for path in ["/news.html", "/news", "/media/news"]:
            potential_url = f"{base_url}{path}"
            logger.info(f"Returning URL: {potential_url}")
            return potential_url
        
        # If no news path is found, return the base URL
        logger.info(f"No specific news path found, returning base URL: {base_url}")
        return base_url
    
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