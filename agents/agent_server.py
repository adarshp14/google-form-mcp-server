"""
Agent Server for CamelAIOrg Integration with Google Forms MCP

This module provides a Flask-based REST API that accepts natural language requests,
processes them through the FormAgent, and returns the results.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import logging

from agent_integration import FormAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_server")

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize form agent
form_agent = FormAgent()

# Configuration
PORT = int(os.getenv('PORT', 5001))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "service": "CamelAIOrg Agent Server",
        "version": "1.0.0"
    })

@app.route('/process', methods=['POST'])
def process_request():
    """
    Process a natural language request by passing it to the FormAgent.
    The FormAgent is responsible for NLP and interacting with the MCP server.
    
    Request format:
    {
        "request_text": "Create a feedback form with 3 questions"
    }
    
    Response format (on success):
    {
        "status": "success",
        "result": { ... form details ... }
    }
    Response format (on error):
    {
        "status": "error",
        "message": "Error description"
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request must be JSON"
            }), 400
        
        data = request.get_json()
        
        if 'request_text' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameter 'request_text'"
            }), 400
        
        request_text = data['request_text']
        logger.info(f"Agent server received request: {request_text}")
        
        # Process the request through the FormAgent
        # The FormAgent's process_request method will handle NLP,
        # MCP packet creation, and communication with the MCP server.
        result = form_agent.process_request(request_text)
        
        # The agent's response (success or error) is returned directly
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Internal Agent Server Error: {str(e)}"
        }), 500

@app.route('/schema', methods=['GET'])
def get_schema():
    """Return the agent capabilities schema."""
    schema = {
        "name": "Google Forms Creator Agent",
        "description": "Creates Google Forms from natural language requests",
        "capabilities": [
            {
                "name": "create_form",
                "description": "Create a new Google Form with questions"
            },
            {
                "name": "add_question",
                "description": "Add a question to an existing form"
            },
            {
                "name": "get_responses",
                "description": "Get responses from an existing form"
            }
        ],
        "example_requests": [
            "Create a customer feedback form with rating questions",
            "Make a survey about remote work preferences",
            "Set up an RSVP form for my event"
        ]
    }
    
    return jsonify({
        "status": "success",
        "schema": schema
    })

# Run the Flask app
if __name__ == '__main__':
    logger.info(f"Starting CamelAIOrg Agent Server on port {PORT}")
    logger.info(f"Debug mode: {DEBUG}")
    
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG) 