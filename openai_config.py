import os
from openai import OpenAI
# Create a completely clean configuration with no proxy settings
def get_openai_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        http_client=None  # Force creating a new client with no proxies
    )
# Create a global client instance
client = get_openai_client()