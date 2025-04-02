import logging
import random
import re
from typing import Dict, List, Optional, Any

import requests
import trafilatura
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User agents to rotate for avoiding blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]


def get_random_user_agent():
    """Return a random user agent from the list"""
    return random.choice(USER_AGENTS)


def scrape_latest_articles(base_url: str, max_articles: int = 10) -> List[Dict[str, Any]]:
    """
    Scrape the latest articles from the provided URL
    
    Args:
        base_url: The URL of the college news website
        max_articles: Maximum number of articles to scrape
        
    Returns:
        A list of dictionaries containing article information (headline, text, url)
    """
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        logger.info(f"Scraping articles from {base_url}")
        response = requests.get(base_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            logger.error(f"Failed to access {base_url}, status code: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find news article links - this pattern needs to be adapted to the specific site structure
        articles = []
        article_links = []
        
        # Look for common article container patterns
        article_containers = soup.select('.news-item, .article, .post, .news-article, article, .story')
        
        if not article_containers:
            # Try finding links with news-related text
            all_links = soup.find_all('a', href=True)
            potential_links = [
                link for link in all_links 
                if any(term in link.get_text().lower() for term in ['news', 'story', 'article', 'press'])
                or re.search(r'/(news|stories|articles|press-releases|updates)/[^/]+', link['href'])
            ]
            
            # Filter to only keep links to articles
            for link in potential_links:
                href = link.get('href', '')
                if not href.startswith('http'):
                    # Make relative URLs absolute
                    if href.startswith('/'):
                        href = base_url.rstrip('/') + href
                    else:
                        href = base_url.rstrip('/') + '/' + href
                
                if href not in article_links and not href.endswith(('.pdf', '.docx', '.xlsx')):
                    article_links.append(href)
                    
                # Stop when we reach the max number of articles
                if len(article_links) >= max_articles:
                    break
        else:
            # Extract links from article containers
            for container in article_containers[:max_articles]:
                link_tag = container.find('a', href=True)
                if link_tag:
                    href = link_tag.get('href', '')
                    if not href.startswith('http'):
                        # Make relative URLs absolute
                        if href.startswith('/'):
                            href = base_url.rstrip('/') + href
                        else:
                            href = base_url.rstrip('/') + '/' + href
                    
                    if href not in article_links:
                        article_links.append(href)
                        
                    # Get headline from link or container
                    headline = link_tag.get_text().strip()
                    if not headline:
                        headline_tag = container.find(['h1', 'h2', 'h3', 'h4'])
                        if headline_tag:
                            headline = headline_tag.get_text().strip()
                    
                    if headline:
                        article = {
                            'headline': headline,
                            'url': href
                        }
                        articles.append(article)
        
        # If we extracted links but not full article data, process each link
        if article_links and not articles:
            for url in article_links[:max_articles]:
                try:
                    # Try to get the article content
                    article_text = scrape_article_text(url)
                    if article_text:
                        # Extract a headline from the title tag or first heading
                        response = requests.get(url, headers=headers, timeout=10)
                        article_soup = BeautifulSoup(response.text, 'html.parser')
                        
                        headline = article_soup.title.string if article_soup.title else None
                        if not headline:
                            heading = article_soup.find(['h1', 'h2'])
                            headline = heading.get_text().strip() if heading else "Article"
                        
                        # Remove site name from headline if present
                        headline = re.sub(r'\s*\|\s*.*$', '', headline)
                        headline = re.sub(r'\s*-\s*.*$', '', headline)
                        
                        articles.append({
                            'headline': headline,
                            'text': article_text,
                            'url': url
                        })
                except Exception as e:
                    logger.error(f"Error scraping article {url}: {str(e)}")
                    continue
        
        # For articles that were found but without text, get the full text
        for article in articles:
            if 'text' not in article:
                try:
                    article['text'] = scrape_article_text(article['url'])
                except Exception as e:
                    logger.error(f"Error getting text for article {article['url']}: {str(e)}")
                    article['text'] = "Content unavailable"
        
        logger.info(f"Successfully scraped {len(articles)} articles")
        return articles
    
    except Exception as e:
        logger.error(f"Error scraping articles from {base_url}: {str(e)}")
        return []


def scrape_article_text(article_url: str) -> Optional[str]:
    """
    Scrape the content of an individual article using trafilatura
    for more reliable content extraction
    
    Args:
        article_url: The URL of the article
        
    Returns:
        The article text content or None if failed
    """
    try:
        headers = {"User-Agent": get_random_user_agent()}
        
        # Use trafilatura for extraction
        downloaded = trafilatura.fetch_url(article_url, headers=headers)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if text:
                return text
        
        # Fallback to BeautifulSoup if trafilatura fails
        response = requests.get(article_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and other non-content elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Try to find the main content area
            main_content = soup.select_one('main, #content, .content, article, .post, .article')
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                # If we can't find a specific content area, just get the body text
                text = soup.body.get_text(separator='\n', strip=True) if soup.body else ''
            
            # Clean up the text
            text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines
            return text
        
        return None
    
    except Exception as e:
        logger.error(f"Error extracting article content from {article_url}: {str(e)}")
        return None