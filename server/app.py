from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import requests # Import requests library

from mcp_handler import MCPHandler
from utils.logger import log_mcp_request, log_mcp_response, log_error, get_logger
import config
from forms_api import GoogleFormsAPI

# Initialize Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the MCP handler
mcp_handler = MCPHandler()
logger = get_logger()
forms_api = GoogleFormsAPI()

@app.route('/')
def index():
    """Render the main page of the application."""
    return render_template('index.html')

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Return the MCP tools schema."""
    try:
        schema = mcp_handler.get_tools_schema()
        return jsonify({
            "status": "success",
            "tools": schema,
            "version": config.MCP_VERSION
        })
    except Exception as e:
        log_error("Error returning schema", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/process', methods=['POST'])
def process_mcp_request():
    """Process an MCP request."""
    try:
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Request must be JSON"
            }), 400
        
        request_data = request.get_json()
        log_mcp_request(request_data)
        
        response = mcp_handler.process_request(request_data)
        log_mcp_response(response)
        
        return jsonify(response)
    
    except Exception as e:
        log_error("Error processing MCP request", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "version": config.MCP_VERSION
    })

# WebSocket for real-time UI updates
@app.route('/ws')
def websocket():
    """WebSocket endpoint for real-time updates."""
    return render_template('websocket.html')

@app.route('/api/forms', methods=['POST'])
def forms_api():
    """Handle form operations."""
    try:
        data = request.json
        action = data.get('action')
        
        logger.info(f"Received form API request: {action}")
        
        if action == 'create_form':
            title = data.get('title', 'Untitled Form')
            description = data.get('description', '')
            
            logger.info(f"Creating form with title: {title}")
            result = forms_api.create_form(title, description)
            logger.info(f"Form created with ID: {result.get('form_id')}")
            logger.info(f"Form response URL: {result.get('response_url')}")
            logger.info(f"Form edit URL: {result.get('edit_url')}")
            
            return jsonify({"status": "success", "result": result})
        
        return jsonify({"status": "error", "message": f"Unknown action: {action}"})
    except Exception as e:
        logger.error(f"Error in forms API: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/agent_proxy', methods=['POST'])
def agent_proxy():
    """Proxy requests from the frontend to the agent server."""
    try:
        frontend_data = request.get_json()
        if not frontend_data or 'request_text' not in frontend_data:
            log_error("Agent proxy received invalid data from frontend", frontend_data)
            return jsonify({"status": "error", "message": "Invalid request data"}), 400

        agent_url = config.AGENT_ENDPOINT
        if not agent_url:
             log_error("Agent endpoint URL is not configured.", None)
             return jsonify({"status": "error", "message": "Agent service URL not configured."}), 500
        
        logger.info(f"Proxying request to agent at {agent_url}: {frontend_data}")

        # Forward the request to the agent server
        # Note: Consider adding timeout and error handling for the requests.post call
        agent_response = requests.post(
            agent_url,
            json=frontend_data, 
            headers={'Content-Type': 'application/json'}
            # Potentially add API key header if agent requires it: 
            # headers={"Authorization": f"Bearer {config.AGENT_API_KEY}"}
        )
        
        # Check agent response status
        agent_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        agent_data = agent_response.json()
        logger.info(f"Received response from agent: {agent_data}")
        
        # Return the agent's response directly to the frontend
        return jsonify(agent_data)

    except requests.exceptions.RequestException as e:
        log_error(f"Error communicating with agent server at {config.AGENT_ENDPOINT}", e)
        return jsonify({"status": "error", "message": f"Failed to reach agent service: {str(e)}"}), 502 # Bad Gateway
    except Exception as e:
        log_error("Error in agent proxy endpoint", e)
        return jsonify({"status": "error", "message": f"Internal proxy error: {str(e)}"}), 500

if __name__ == '__main__':
    port = config.PORT
    debug = config.DEBUG
    
    logger.info(f"Starting Google Forms MCP Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
