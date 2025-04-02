import json
import logging
import os
import time
from typing import Dict, List, Optional, Any

from flask import Flask, jsonify, render_template, send_from_directory, request
from dotenv import load_dotenv

from scraper import scrape_latest_articles
from summarizer import summarize_article, analyze_sentiment
from utils import get_college_url, format_output, get_host_url

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)


@app.route('/')
def root():
    """
    Root endpoint that displays documentation about the API
    """
    host_url = get_host_url()
    
    return render_template('index.html', host_url=host_url)


@app.route('/latest-news')
def get_latest_news():
    """
    Retrieve and summarize the latest news articles for a specific college
    """
    # Get the college name from the query parameters
    college_name = request.args.get('college')
    if not college_name:
        return jsonify({
            "error": "Missing required parameter: college",
            "message": "Please provide a Clemson University college name"
        }), 400
    
    try:
        # Validate and get the college URL
        college_url = get_college_url(college_name)
        
        # Scrape the latest articles (max 10 for latest news)
        start_time = time.time()
        logger.info(f"Scraping articles from {college_url} for {college_name}")
        articles = scrape_latest_articles(college_url, max_articles=10)
        logger.info(f"Found {len(articles)} articles in {time.time() - start_time:.2f} seconds")
        
        if not articles:
            # If no articles were found, return a meaningful response
            return jsonify({
                "college": college_name,
                "result": f"No recent news articles found for {college_name}."
            })
        
        # Process each article - summarize and analyze sentiment
        processed_articles = []
        for article in articles:
            # Extract the article headline, content, and URL
            headline = article.get('headline', 'Untitled Article')
            content = article.get('text', '')
            url = article.get('url', '#')
            
            # Summarize the article text
            if content:
                logger.info(f"Summarizing article: {headline[:50]}...")
                summary, rewritten_headline = summarize_article(headline, content)
                
                # Analyze sentiment
                sentiment = analyze_sentiment(content)
                
                processed_articles.append({
                    'headline': headline,
                    'rewritten_headline': rewritten_headline,
                    'summary': summary,
                    'url': url,
                    'sentiment': sentiment
                })
        
        # Format the output as markdown text
        result = format_output(college_name, processed_articles)
        
        # Return the result
        return jsonify({
            "college": college_name,
            "result": result
        })
    
    except ValueError as e:
        # Handle invalid college names
        return jsonify({
            "error": "Invalid college name",
            "message": str(e)
        }), 400
    
    except Exception as e:
        # Log and handle any other errors
        logger.error(f"Error retrieving news: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve news",
            "message": f"An error occurred: {str(e)}"
        }), 500


@app.route('/.well-known/ai-plugin.json')
def get_plugin_manifest():
    """
    Return the plugin manifest for OpenAI
    """
    host = get_host_url()
    
    return jsonify({
        "schema_version": "v1",
        "name_for_human": "Clemson GPT News",
        "name_for_model": "clemson_gpt_news",
        "description_for_human": "Get the latest news and summaries from Clemson University colleges.",
        "description_for_model": "Get the latest news and summaries from Clemson University colleges.",
        "auth": {
            "type": "none"
        },
        "api": {
            "type": "openapi",
            "url": f"{host}/openapi.json"
        },
        "logo_url": f"{host}/static/logo.svg",
        "contact_email": "support@example.com",
        "legal_info_url": "https://example.com/legal"
    })


@app.route('/openapi.json')
def get_openapi_spec():
    """
    Return the OpenAPI specification
    """
    host = get_host_url()
    
    spec = {
        "openapi": "3.0.1",
        "info": {
            "title": "Clemson GPT News API",
            "description": "API for retrieving and summarizing news from Clemson University colleges",
            "version": "v1"
        },
        "servers": [
            {
                "url": host
            }
        ],
        "paths": {
            "/latest-news": {
                "get": {
                    "operationId": "get_latest_news",
                    "summary": "Get the latest news and summaries from a Clemson University college",
                    "parameters": [
                        {
                            "name": "college",
                            "in": "query",
                            "description": "The name of the Clemson University college",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": list(["College of Agriculture, Forestry and Life Sciences",
                                             "College of Architecture, Art and Construction",
                                             "College of Arts and Humanities",
                                             "College of Behavioral, Social and Health Sciences",
                                             "College of Education",
                                             "College of Engineering, Computing and Applied Sciences",
                                             "College of Science",
                                             "Harvey S. Peeler Jr. College of Veterinary Medicine",
                                             "Wilbur O. and Ann Powers College of Business"])
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "college": {
                                                "type": "string",
                                                "description": "The name of the college"
                                            },
                                            "result": {
                                                "type": "string",
                                                "description": "The news summaries in markdown format"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "400": {
                            "description": "Bad Request",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string"
                                            },
                                            "message": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "500": {
                            "description": "Server Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "error": {
                                                "type": "string"
                                            },
                                            "message": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    return jsonify(spec)


@app.route('/static/<path:path>')
def serve_static(path):
    """
    Serve static files
    """
    return send_from_directory('static', path)


if __name__ == "__main__":
    # Ensure required environment variables are set
    if not os.environ.get("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY environment variable not set!")
    
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
