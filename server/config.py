import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google API settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REFRESH_TOKEN = os.getenv('GOOGLE_REFRESH_TOKEN')

# API scopes needed for Google Forms
# Include more scopes to ensure proper access
SCOPES = [
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata'
]

# Server settings
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# CamelAIOrg Agent settings
AGENT_ENDPOINT = os.getenv('AGENT_ENDPOINT', 'http://agents:5001/process')
AGENT_API_KEY = os.getenv('AGENT_API_KEY')

# MCP Protocol settings
MCP_VERSION = "1.0.0"
MCP_TOOLS = [
    "create_form",
    "add_question",
    "get_responses"
]

# LLM Settings / Gemini Settings (Update this section)
# REMOVE LLM_API_KEY and LLM_API_ENDPOINT
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# The specific model endpoint will be constructed in the agent
