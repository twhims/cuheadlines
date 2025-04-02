from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from openai_service import OpenAIService

router = APIRouter()

# Initialize the OpenAI service
openai_service = OpenAIService()

class TextRequest(BaseModel):
    text: str
    max_tokens: Optional[int] = 150

class TextResponse(BaseModel):
    result: str

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    rating: int
    confidence: float

@router.post("/analyze/text", response_model=TextResponse, tags=["Analysis"])
async def analyze_text(request: TextRequest):
    """
    Analyze text using OpenAI's API and return a summary or analysis
    """
    try:
        result = openai_service.summarize_text(request.text)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze text: {str(e)}")

@router.post("/analyze/sentiment", response_model=SentimentResponse, tags=["Analysis"])
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze the sentiment of the provided text and return a rating (1-5) and confidence score
    """
    try:
        result = openai_service.analyze_sentiment(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze sentiment: {str(e)}")

@router.post("/generate/response", response_model=TextResponse, tags=["Generation"])
async def generate_response(request: TextRequest):
    """
    Generate a response to the given text using OpenAI's API
    """
    try:
        result = openai_service.generate_response(request.text, request.max_tokens)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@router.get("/health", tags=["System"])
async def health_check():
    """
    Check if the API is healthy and the OpenAI connection is working
    """
    if os.getenv("OPENAI_API_KEY"):
        return {"status": "healthy", "openai_configured": True}
    return {"status": "healthy", "openai_configured": False}
