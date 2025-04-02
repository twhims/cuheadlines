#!/bin/bash

# Load environment variables from .env file
source .env

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY environment variable is not set!"
    echo "Please set it in your .env file or export it in your shell."
    exit 1
fi

# Start the server with Uvicorn (alternative to Flask's development server)
uvicorn main:app --host 0.0.0.0 --port 5000 --reload