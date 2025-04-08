import json
import uuid
from forms_api import GoogleFormsAPI
import config

class MCPHandler:
    """
    Handler for Model Context Protocol (MCP) packets.
    
    Processes incoming MCP requests for Google Forms operations and returns
    appropriately formatted MCP responses.
    """
    
    def __init__(self):
        """Initialize the MCP handler with a GoogleFormsAPI instance."""
        self.forms_api = GoogleFormsAPI()
        self.version = config.MCP_VERSION
        self.tools = config.MCP_TOOLS
    
    def get_tools_schema(self):
        """Return the schema for all available tools."""
        return {
            "create_form": {
                "description": "Creates a new Google Form",
                "parameters": {
                    "title": {
                        "type": "string",
                        "description": "The title of the form"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description for the form"
                    }
                },
                "required": ["title"]
            },
            "add_question": {
                "description": "Adds a question to an existing Google Form",
                "parameters": {
                    "form_id": {
                        "type": "string",
                        "description": "The ID of the form to add the question to"
                    },
                    "question_type": {
                        "type": "string",
                        "description": "The type of question (text, paragraph, multiple_choice, checkbox)",
                        "enum": ["text", "paragraph", "multiple_choice", "checkbox"]
                    },
                    "title": {
                        "type": "string",
                        "description": "The question title/text"
                    },
                    "options": {
                        "type": "array",
                        "description": "Options for multiple choice or checkbox questions",
                        "items": {
                            "type": "string"
                        }
                    },
                    "required": {
                        "type": "boolean",
                        "description": "Whether the question is required",
                        "default": False
                    }
                },
                "required": ["form_id", "question_type", "title"]
            },
            "get_responses": {
                "description": "Gets responses for a Google Form",
                "parameters": {
                    "form_id": {
                        "type": "string",
                        "description": "The ID of the form to get responses for"
                    }
                },
                "required": ["form_id"]
            }
        }
    
    def process_request(self, request_data):
        """
        Process an incoming MCP request.
        
        Args:
            request_data: Dict containing the MCP request data
            
        Returns:
            dict: MCP response packet
        """
        try:
            # Extract MCP request components
            transaction_id = request_data.get('transaction_id', str(uuid.uuid4()))
            tool_name = request_data.get('tool_name')
            parameters = request_data.get('parameters', {})
            
            # Validate tool name
            if tool_name not in self.tools:
                return self._create_error_response(
                    transaction_id,
                    f"Unknown tool '{tool_name}'. Available tools: {', '.join(self.tools)}"
                )
            
            # Process the request based on the tool name
            if tool_name == "create_form":
                return self._handle_create_form(transaction_id, parameters)
            elif tool_name == "add_question":
                return self._handle_add_question(transaction_id, parameters)
            elif tool_name == "get_responses":
                return self._handle_get_responses(transaction_id, parameters)
            
            # Shouldn't reach here due to validation above
            return self._create_error_response(transaction_id, f"Tool '{tool_name}' not implemented")
        
        except Exception as e:
            return self._create_error_response(
                request_data.get('transaction_id', str(uuid.uuid4())),
                f"Error processing request: {str(e)}"
            )
    
    def _handle_create_form(self, transaction_id, parameters):
        """Handle a create_form MCP request."""
        if 'title' not in parameters:
            return self._create_error_response(transaction_id, "Missing required parameter 'title'")
        
        title = parameters['title']
        description = parameters.get('description', "")
        
        result = self.forms_api.create_form(title, description)
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "result": result
        }
    
    def _handle_add_question(self, transaction_id, parameters):
        """Handle an add_question MCP request."""
        # Validate required parameters
        required_params = ['form_id', 'question_type', 'title']
        for param in required_params:
            if param not in parameters:
                return self._create_error_response(transaction_id, f"Missing required parameter '{param}'")
        
        # Extract parameters
        form_id = parameters['form_id']
        question_type = parameters['question_type']
        title = parameters['title']
        options = parameters.get('options', [])
        required = parameters.get('required', False)
        
        # Validate question type
        valid_types = ['text', 'paragraph', 'multiple_choice', 'checkbox']
        if question_type not in valid_types:
            return self._create_error_response(
                transaction_id,
                f"Invalid question_type '{question_type}'. Valid types: {', '.join(valid_types)}"
            )
        
        # Validate options for choice questions
        if question_type in ['multiple_choice', 'checkbox'] and not options:
            return self._create_error_response(
                transaction_id,
                f"Options are required for '{question_type}' questions"
            )
        
        result = self.forms_api.add_question(form_id, question_type, title, options, required)
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "result": result
        }
    
    def _handle_get_responses(self, transaction_id, parameters):
        """Handle a get_responses MCP request."""
        if 'form_id' not in parameters:
            return self._create_error_response(transaction_id, "Missing required parameter 'form_id'")
        
        form_id = parameters['form_id']
        result = self.forms_api.get_responses(form_id)
        
        return {
            "transaction_id": transaction_id,
            "status": "success",
            "result": result
        }
    
    def _create_error_response(self, transaction_id, error_message):
        """Create an MCP error response."""
        return {
            "transaction_id": transaction_id,
            "status": "error",
            "error": {
                "message": error_message
            }
        }
