"""
This module contains utility functions for resolving college name references 
when the primary news sources are unavailable.
"""

import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map of college names to their alternative websites
COLLEGE_ALT_URLS = {
    "College of Agriculture, Forestry and Life Sciences": "https://www.clemson.edu/cafls/",
    "College of Architecture, Art and Construction": "https://www.clemson.edu/cah/",
    "College of Arts and Humanities": "https://www.clemson.edu/cah/",
    "College of Behavioral, Social and Health Sciences": "https://www.clemson.edu/cbshs/",
    "College of Education": "https://www.clemson.edu/education/",
    "College of Engineering, Computing and Applied Sciences": "https://www.clemson.edu/cecas/",
    "College of Science": "https://www.clemson.edu/science/",
    "Harvey S. Peeler Jr. College of Veterinary Medicine": "https://www.clemson.edu/cafls/departments/peeler-vet-med/",
    "Wilbur O. and Ann Powers College of Business": "https://www.clemson.edu/business/"
}

# We no longer need specific fallback messages since we've improved the function to include website links dynamically
COLLEGE_FALLBACK_MESSAGES = {}

def get_alt_college_url(college_name: str) -> Optional[str]:
    """
    Get an alternative URL for a college website when the news site is unavailable
    
    Args:
        college_name: The name of the college
    
    Returns:
        An alternative URL for the college or None if not found
    """
    return COLLEGE_ALT_URLS.get(college_name)

def get_fallback_message(college_name: str) -> str:
    """
    Get a fallback message for a college when no news is available
    
    Args:
        college_name: The name of the college
    
    Returns:
        A formatted message explaining that no news is available
    """
    if college_name in COLLEGE_FALLBACK_MESSAGES:
        return COLLEGE_FALLBACK_MESSAGES[college_name]
    
    # Get the alternative URL for this college if available
    alt_url = get_alt_college_url(college_name)
    website_link = f"at {alt_url}" if alt_url else ""
    
    return f"""
# Latest News from {college_name}

At this time, there are no recent news headlines available from the Clemson University {college_name}.

The news.clemson.edu website may be temporarily unavailable or restricting automated access.

Please visit the college website directly {website_link} for the latest information, or check back later when the news feed is accessible again.
"""