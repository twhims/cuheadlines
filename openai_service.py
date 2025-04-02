import json
import os
from openai import OpenAI
from typing import Dict, Any

class OpenAIService:
    def __init__(self):
        """
        Initialize the OpenAI service with the API key from environment variables
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def summarize_text(self, text: str) -> str:
        """
        Summarize the provided text using OpenAI's API
        
        Args:
            text: The text to summarize
            
        Returns:
            A string containing the summarized text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                    {"role": "user", "content": f"Please summarize the following text concisely while maintaining key points:\n\n{text}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to summarize text: {str(e)}")
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of the provided text
        
        Args:
            text: The text to analyze
            
        Returns:
            A dictionary with sentiment rating (1-5) and confidence score
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis expert. "
                        + "Analyze the sentiment of the text and provide a rating "
                        + "from 1 to 5 stars and a confidence score between 0 and 1. "
                        + "Respond with JSON in this format: "
                        + "{'rating': number, 'confidence': number}"
                    },
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return {
                "rating": max(1, min(5, round(result["rating"]))),
                "confidence": max(0, min(1, result["confidence"]))
            }
        except Exception as e:
            raise Exception(f"Failed to analyze sentiment: {str(e)}")
    
    def generate_response(self, text: str, max_tokens: int = 150) -> str:
        """
        Generate a response to the given text
        
        Args:
            text: The input text
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            A string containing the generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": text}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
