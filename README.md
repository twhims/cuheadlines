# Clemson GPT News API

A Python API that provides summarized news articles from Clemson University colleges using the OpenAI API. This project can be configured as an OpenAI action/plugin through the action.yaml configuration file.

## Current Status

**Important Note**: As of April 2025, Clemson University's news website (news.clemson.edu) has implemented anti-scraping measures that prevent the automatic retrieval of news articles. This affects all colleges in the API. As a fallback, the API will return a message directing users to the official college websites.

## Features

- API endpoint to retrieve news from specific Clemson University colleges
- Fallback mechanisms to handle anti-scraping measures
- OpenAI integration for article summarization and sentiment analysis
- OpenAI plugin support through action.yaml and OpenAPI specification

## API Endpoints

### Get Latest News

```
GET /latest-news?college={college_name}
```

This endpoint retrieves the latest news for a specific Clemson University college.

**Parameters**:
- `college` (required): The name of the Clemson University college

**Supported colleges**:
- College of Agriculture, Forestry and Life Sciences
- College of Architecture, Art and Construction 
- College of Arts and Humanities
- College of Behavioral, Social and Health Sciences
- College of Education
- College of Engineering, Computing and Applied Sciences
- College of Science
- Harvey S. Peeler Jr. College of Veterinary Medicine
- Wilbur O. and Ann Powers College of Business

## Environment Variables

Create a `.env` file based on the provided `.env.example`:

```
# OpenAI API Key for article summarization (required)
OPENAI_API_KEY=your_openai_api_key_here

# Host URL for the application (used in API documentation)
# For local development, this will default to http://localhost:5000
# HOST=https://your-deployment-url.com
```

## Running Locally

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key
4. Run the application: `python main.py` or `gunicorn --bind 0.0.0.0:5000 main:app`

## Deployment

The application can be deployed to Render.com using the provided `render.yaml` file:

1. Push your code to GitHub
2. Create a new Web Service on Render.com
3. Connect your GitHub repository
4. Render will automatically use the `render.yaml` configuration
5. Add your OPENAI_API_KEY as an environment variable in the Render dashboard

## Using as an OpenAI Action/Plugin

1. Deploy the application (or run it locally)
2. In the ChatGPT UI, navigate to the Plugin Store
3. Select "Develop your own plugin"
4. Enter your application URL (e.g., https://your-app.onrender.com)
5. Follow the prompts to install the plugin

## Troubleshooting

If you're encountering 403 Forbidden errors when trying to scrape news.clemson.edu, this is due to anti-scraping measures implemented by the university. The API will automatically provide fallback messages with links to the official college websites.

## Future Improvements

- Implement alternative data sources that don't have scraping restrictions
- Add RSS feed support for colleges that provide it
- Create a caching mechanism to reduce API usage and improve response times
