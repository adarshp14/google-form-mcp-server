import logging
import sys
import json
from datetime import datetime

# Configure logger
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)


def log_mcp_request(request_data):
    """Log an incoming MCP request."""
    try:
        transaction_id = request_data.get('transaction_id', 'unknown')
        tool_name = request_data.get('tool_name', 'unknown')
        
        logger.info(f"MCP Request [{transaction_id}] - Tool: {tool_name}")
        logger.debug(f"Request data: {json.dumps(request_data, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error logging MCP request: {str(e)}")


def log_mcp_response(response_data):
    """Log an outgoing MCP response."""
    try:
        transaction_id = response_data.get('transaction_id', 'unknown')
        status = response_data.get('status', 'unknown')
        
        logger.info(f"MCP Response [{transaction_id}] - Status: {status}")
        logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
        
    except Exception as e:
        logger.error(f"Error logging MCP response: {str(e)}")


def log_error(message, error=None):
    """Log an error."""
    try:
        if error:
            logger.error(f"{message}: {str(error)}")
        else:
            logger.error(message)
    except Exception as e:
        # Last resort if logging itself fails
        print(f"Logging error: {str(e)}")


def get_logger():
    """Get the configured logger."""
    return logger
