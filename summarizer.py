import logging
import os
from typing import Dict, Optional, Tuple, Any

from openai_config import client


def summarize_article(headline: str, content: str) -> Tuple[str, str]:
    """
    Summarize an article using OpenAI GPT
    
    Args:
        headline: The headline of the article
        content: The full text of the article
        
    Returns:
        A tuple containing (summary, rewritten_headline)
    """
    if not content:
        return "No content available to summarize.", headline
    
    # Truncate content if it's too long (to avoid token limits)
    max_content_length = 8000
    if len(content) > max_content_length:
        truncated_content = content[:max_content_length] + "..."
    else:
        truncated_content = content
    
    try:
        # Prompt for GPT to generate a summary and headline
        prompt = f"""
        Original Headline: {headline}
        
        Article Content: {truncated_content}
        
        Task: Create a concise 2-sentence summary of this article that captures the key points.
        Also, suggest an engaging rewritten headline that would appeal to Clemson University students and faculty.
        
        Format your response as:
        Summary: [Your 2-sentence summary here]
        Rewritten Headline: [Your engaging headline here]
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {"role": "system", "content": "You are a skilled journalist who specializes in creating engaging summaries and headlines for college news articles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Parse the result
        result = response.choices[0].message.content.strip()
        
        # Extract the summary and rewritten headline
        summary_match = result.split("Summary:", 1)
        if len(summary_match) > 1:
            raw_summary = summary_match[1].split("Rewritten Headline:", 1)[0].strip()
        else:
            raw_summary = "Summary not available."
        
        headline_match = result.split("Rewritten Headline:", 1)
        if len(headline_match) > 1:
            rewritten_headline = headline_match[1].strip()
        else:
            rewritten_headline = headline  # Keep original if no rewrite found
        
        return raw_summary, rewritten_headline
    
    except Exception as e:
        logger.error(f"Error summarizing article: {str(e)}")
        return f"Error generating summary: {str(e)}", headline


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of the provided text
    
    Args:
        text: The text to analyze
        
    Returns:
        A dictionary with sentiment rating (1-5) and confidence score
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
            messages=[
                {
                    "role": "system",
                    "content": "You are a sentiment analysis expert. "
                    + "Analyze the sentiment of the text and provide a rating "
                    + "from 1 to 5 stars (where 5 is very positive) and a confidence score between 0 and 1. "
                    + "Respond with JSON in this format: "
                    + "{'rating': number, 'confidence': number, 'explanation': 'brief reason'}"
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            max_tokens=150
        )
        
        # Parse the sentiment analysis result
        result = response.choices[0].message.content
        # Convert to Python dictionary
        import json
        sentiment_data = json.loads(result)
        
        return {
            "rating": max(1, min(5, round(sentiment_data.get("rating", 3)))),
            "confidence": max(0, min(1, sentiment_data.get("confidence", 0.5))),
            "explanation": sentiment_data.get("explanation", "No explanation provided")
        }
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return {
            "rating": 3,
            "confidence": 0.0,
            "explanation": f"Error analyzing sentiment: {str(e)}"
        }
