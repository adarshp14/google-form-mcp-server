"""
CamelAIOrg Agent Integration for Google Forms MCP Server

This module provides integration with CamelAIOrg's agent framework,
enabling natural language processing to create Google Forms through MCP.
"""

import os
import json
import logging
import requests
import datetime

# REMOVE: Import our mock CamelAI implementation
# from camelai import create_agent

# Load environment variables
# load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_integration")

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://mcp-server:5000/api/process')
AGENT_API_KEY = os.getenv('AGENT_API_KEY', 'demo_key') # Might be used for a real LLM API key

# Import Camel AI components (assuming structure)
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.types import ModelPlatformType, ModelType, RoleType # Added RoleType
from camel.models import ModelFactory

class FormAgent:
    """
    Agent for handling natural language form creation requests.
    Uses NLP (simulated via _call_llm_agent) to process natural language
    and convert it to MCP tool calls.
    """
    
    def __init__(self):
        """Initialize the agent."""
        self.logger = logger
        self.log_entries = [] # Initialize log storage
        # REMOVE: self.camel_agent = create_agent("FormAgent", ...)
        self.logger.info("FormAgent initialized (using simulated LLM)")

    def _log_step(self, step_type, data):
        """Adds a structured log entry for the frontend."""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step_type": step_type, 
            "data": data
        }
        self.log_entries.append(entry)
        # Also log to server console for debugging
        self.logger.info(f"AGENT LOG STEP: {step_type} - {data}") 
    
    def process_request(self, request_text):
        """
        Processes a natural language request using a simulated LLM call.
        1. Calls a simulated LLM to parse the request into structured JSON.
        2. Determines the necessary MCP tool calls based on the JSON.
        3. Executes the tool calls by sending requests to the MCP server.
        4. Orchestrates multi-step processes.
        5. Returns the final result or error.
        """
        self.log_entries = [] # Clear log for new request
        self._log_step("Request Received", {"text": request_text})
        
        try:
            # 1. Analyze request using simulated LLM call
            self._log_step("NLP Analysis Start", {})
            structured_form_data = self._call_llm_agent(request_text)
            self.logger.info(f"Simulated LLM Structured Output: {json.dumps(structured_form_data, indent=2)}")
            self._log_step("NLP Analysis Complete", {"structured_data": structured_form_data})
            
            # Basic validation of LLM output
            if not structured_form_data or 'formTitle' not in structured_form_data:
                 self.logger.error("Simulated LLM did not return valid structured data.")
                 return { "status": "error", "message": "Failed to understand the request structure using LLM." }

            # Extract sections and settings - Basic structure assumes one form for now
            form_params = {
                "title": structured_form_data.get('formTitle'),
                "description": structured_form_data.get('formDescription', '')
                # We would also handle settings here if the API supported it
            }
            sections = structured_form_data.get('sections', [])
            if not sections:
                 self.logger.error("Simulated LLM did not return any form sections/questions.")
                 return { "status": "error", "message": "LLM did not identify any questions for the form." }

            # 2. Determine and execute tool calls (simplified flow: create form, add all questions)
            # NOTE: This doesn't handle multiple sections, logic, or advanced settings yet
            all_questions = []
            for section in sections:
                # TODO: Add support for creating sections/page breaks if API allows
                # self.logger.info(f"Processing section: {section.get('title', 'Untitled Section')}")
                all_questions.extend(section.get('questions', []))
            
            # Pass the extracted questions to the creation flow
            form_params['questions'] = all_questions
            # Execute the flow, which will populate self.log_entries further
            final_response = self._execute_create_form_flow(form_params)

            # Add the collected logs to the final response if successful
            if final_response.get("status") == "success":
                 final_response["log_entries"] = self.log_entries
            
            return final_response
        
        except Exception as e:
            self.logger.error(f"Error in FormAgent process_request: {str(e)}", exc_info=True)
            self._log_step("Agent Error", {"error": str(e)})
            # Include logs gathered so far in the error response too
            return {
                "status": "error",
                "message": f"Agent failed to process request: {str(e)}",
                "log_entries": self.log_entries
            }

    def _call_llm_agent(self, request_text):
        """
        Uses Camel AI's ChatAgent to process the request and extract structured data.
        Falls back to a basic structure if the LLM call fails.
        """
        # Check for the API key first (using the name Camel AI expects)
        api_key = os.getenv('GOOGLE_API_KEY') 
        if not api_key:
            self.logger.error("GOOGLE_API_KEY is not set in the environment.") # Updated log message
            return self._get_fallback_structure(request_text)

        try:
            # 1. Setup Model
            # Assuming ModelFactory can find the key from env or we pass it
            # Adjust ModelType enum based on actual Camel AI definition if needed
            # Using a placeholder like ModelType.GEMINI_1_5_FLASH - this will likely need correction
            model_name_str = "gemini-1.5-flash-latest" # Keep the string name
            # Attempt to create model instance via factory
            # Create the required config dict - make it empty and rely on env var GOOGLE_API_KEY
            model_config_dict = { 
                 # No API key here - expecting library to read GOOGLE_API_KEY from env
            }
            # REVERT: Go back to GEMINI platform type
            llm_model = ModelFactory.create(
                model_platform=ModelPlatformType.GEMINI, 
                model_type=ModelType.GEMINI_1_5_FLASH, 
                model_config_dict=model_config_dict 
            )
            self.logger.info(f"Camel AI Model configured using: {ModelType.GEMINI_1_5_FLASH}")

            # 2. Prepare messages for the ChatAgent
            system_prompt = self._build_llm_prompt(request_text)
            system_message = BaseMessage(
                role_name="System", 
                role_type=RoleType.ASSISTANT,
                meta_dict=None, 
                content=system_prompt
            )
            user_message = BaseMessage(
                role_name="User",
                role_type=RoleType.USER,
                meta_dict=None,
                content=request_text # Or maybe just a trigger like "Process the request"? Let's try request_text
            )

            # 3. Initialize and run the ChatAgent
            agent = ChatAgent(system_message=system_message, model=llm_model)
            agent.reset() # Ensure clean state

            self.logger.info("Calling Camel AI ChatAgent...")
            response = agent.step(user_message)
            
            if not response or not response.msgs:
                self.logger.error("Camel AI agent did not return a valid response.")
                return self._get_fallback_structure(request_text)

            # 4. Extract JSON content from the last message
            # Assuming the response structure contains a list of messages `msgs`
            # and the agent's reply is the last one.
            agent_reply_message = response.msgs[-1]
            content = agent_reply_message.content
            self.logger.debug(f"Raw Camel AI agent response content: {content}") 

            # --- Robust JSON Extraction --- 
            try:
                # Find the start and end of the JSON object
                json_start = content.find('{')
                json_end = content.rfind('}')
                
                if json_start != -1 and json_end != -1 and json_end > json_start:
                    json_string = content[json_start:json_end+1]
                    structured_data = json.loads(json_string)
                    self.logger.info("Successfully parsed structured JSON from Camel AI agent response.")
                    return structured_data
                else:
                    # Fallback if JSON bounds couldn't be found
                    self.logger.error(f"Could not find valid JSON object boundaries in response. Content: {content}")
                    return self._get_fallback_structure(request_text)

            except json.JSONDecodeError as e:
                 self.logger.error(f"Failed to parse JSON content from Camel AI agent: {e}. Extracted content attempt: {json_string if 'json_string' in locals() else 'N/A'}")
                 return self._get_fallback_structure(request_text)

        except ImportError as e:
             self.logger.error(f"Failed to import Camel AI components. Is 'camel-ai' installed correctly? Error: {e}")
             return self._get_fallback_structure(request_text)
        except Exception as e:
            # Catch potential errors during Camel AI model init or agent step
            self.logger.error(f"Error during Camel AI processing: {str(e)}", exc_info=True)
            return self._get_fallback_structure(request_text)

    def _build_llm_prompt(self, request_text):
        """
        Constructs the detailed prompt for the LLM.
        
        Crucial for getting reliable JSON output.
        Needs careful tuning based on the LLM used.
        """
        # Define the desired JSON structure and supported types/features
        # This helps the LLM understand the target format.
        json_schema_description = """
        { 
          "formTitle": "string",
          "formDescription": "string (optional)",
          "settings": { 
            // Note: Backend does not support settings yet, but LLM can parse them
            "collectEmail": "string (optional: 'required' or 'optional')",
            "limitToOneResponse": "boolean (optional)",
            "progressBar": "boolean (optional)",
            "confirmationMessage": "string (optional)"
          },
          "sections": [ 
            {
              "title": "string",
              "description": "string (optional)",
              "questions": [
                {
                  "title": "string",
                  "description": "string (optional)",
                  "type": "string (enum: text, paragraph, multiple_choice, checkbox, linear_scale, multiple_choice_grid, checkbox_grid)", 
                  "required": "boolean (optional, default: false)",
                  "options": "array of strings (required for multiple_choice, checkbox)" 
                           + " OR object { min: int, max: int, minLabel: string (opt), maxLabel: string (opt) } (required for linear_scale)" 
                           + " OR object { rows: array of strings, columns: array of strings } (required for grids)",
                  "logic": "object { on: string (option value), action: string (enum: submit_form, skip_section), targetSectionTitle: string (required if action=skip_section) } (optional)", // Note: Backend doesn't support logic
                  "validation": "string (optional: 'email' or other types if supported)" // Note: Backend doesn't support validation
                }
                // ... more questions ...
              ]
            }
            // ... more sections ...
          ]
        }
        """
        
        prompt = f"""Analyze the following user request to create a Google Form. Based ONLY on the request, generate a JSON object strictly adhering to the following schema. 

SCHEMA:
```json
{json_schema_description}
```

RULES:
- Output *only* the JSON object, nothing else before or after.
- If the user requests features not supported by the schema description (e.g., file uploads, specific themes, complex scoring), omit them from the JSON.
- If the request is unclear about question types or options, make reasonable assumptions (e.g., use 'text' for simple questions, provide standard options for ratings).
- Ensure the 'options' field matches the required format for the specified 'type'.
- Pay close attention to required fields in the schema description.
- If the request seems too simple or doesn't clearly describe a form, create a basic form structure with a title based on the request and a few generic questions (like Name, Email, Comments).

USER REQUEST:
```
{request_text}
```

JSON OUTPUT:
"""
        return prompt

    def _get_fallback_structure(self, request_text):
         """Returns a basic structure if LLM call fails or parsing fails."""
         self.logger.warning(f"Gemini call/parsing failed. Falling back to basic structure for: {request_text}")
         return {
             "formTitle": self._generate_title(request_text), 
             "formDescription": request_text,
             "settings": {},
             "sections": [
                 {
                     "questions": [
                         {"title": "Name", "type": "text", "required": True},
                         {"title": "Email", "type": "text", "required": False},
                         {"title": "Your Response", "type": "paragraph", "required": True}
                     ]
                 }
             ]
         }

    def _execute_create_form_flow(self, params):
        """
        Handles the complete flow for creating a form and adding its questions.
        """
        self.logger.info(f"Executing create form flow with params: {params}")
        
        # Extract potential questions from NLP parameters
        questions_to_add = params.pop('questions', []) # Remove questions from main params
        
        # A. Create the form first
        self._log_step("Create Form Start", {"params": params})
        create_form_response = self._handle_create_form(params)
        self._log_step("Create Form End", {"response": create_form_response})
        
        if create_form_response.get("status") != "success":
            self.logger.error(f"Form creation failed: {create_form_response.get('message')}")
            return create_form_response # Return the error from create_form
            
        # Get the form_id from the successful response
        form_result = create_form_response.get('result', {})
        form_id = form_result.get('form_id')
        
        if not form_id:
            self.logger.error("Form creation succeeded but no form_id returned.")
            return { "status": "error", "message": "Form created, but form_id missing in response." }
            
        self.logger.info(f"Form created successfully: {form_id}")
        
        # B. Add questions if any were identified by NLP
        question_results = []
        if questions_to_add:
            self._log_step("Add Questions Start", {"count": len(questions_to_add)})
            self.logger.info(f"Adding {len(questions_to_add)} questions to form {form_id}")
            for question_data in questions_to_add:
                question_params = {
                    "form_id": form_id,
                    # Ensure structure matches _handle_add_question needs
                    "type": question_data.get('type'), 
                    "title": question_data.get('title'),
                    "options": question_data.get('options', []), 
                    "required": question_data.get('required', False)
                }
                
                # Validate basic question params before sending
                if not question_params['type'] or not question_params['title']:
                     self.logger.warning(f"Skipping invalid question data: {question_data}")
                     continue
                     
                self._log_step("Add Question Start", {"question_index": questions_to_add.index(question_data), "params": question_params})
                add_q_response = self._handle_add_question(question_params)
                self._log_step("Add Question End", {"question_index": questions_to_add.index(question_data), "response": add_q_response})
                question_results.append(add_q_response)
                
                # Log if the question type wasn't supported by the backend
                if add_q_response.get("status") == "error" and "Invalid question_type" in add_q_response.get("message", ""):
                     self.logger.warning(f"Question '{question_params['title']}' failed: Type '{question_params['type']}' likely not supported by backend API yet.")
                elif add_q_response.get("status") != "success":
                    self.logger.error(f"Failed to add question '{question_params['title']}': {add_q_response.get('message')}")
                
                # Optional: Check if question adding failed and decide whether to stop
                if add_q_response.get("status") != "success":
                    self.logger.error(f"Failed to add question '{question_params['title']}': {add_q_response.get('message')}")
                    # Decide: continue adding others, or return error immediately?
                    # For now, let's continue but log the error.
            self._log_step("Add Questions End", {})
        else:
             self.logger.info(f"No questions identified by NLP to add to form {form_id}")
             self._log_step("Add Questions Skipped", {})

        # 5. Return the final result (details of the created form)
        # We can optionally include the results of adding questions if needed
        final_result = form_result
        # Let's add the questions that were *attempted* to be added back for the UI
        final_result['questions'] = questions_to_add 

        return {
            "status": "success",
            "result": final_result 
            # Optionally add: "question_addition_results": question_results
        }

    # Add the fallback title generation method back (or use a simpler one)
    def _generate_title(self, request_text):
        words = request_text.split()
        if len(words) <= 5:
            return request_text + " Form"
        else:
            return " ".join(words[:5]) + "... Form"
    
    # --- Methods for handling specific tool calls by sending to MCP Server ---

    def _handle_create_form(self, params):
        """
        Handle form creation by sending MCP packet to the server.
        
        Args:
            params: Parameters for form creation
            
        Returns:
            dict: Result of the form creation
        """
        self.logger.info(f"Creating form with params: {params}")
        
        # Prepare MCP packet
        mcp_packet = {
            "tool_name": "create_form",
            "parameters": {
                "title": params.get("title", "Form from NL Request"),
                "description": params.get("description", "")
            }
        }
        
        # Log *before* sending
        self._log_step("MCP Request (create_form)", mcp_packet)
        response = self._send_to_mcp_server(mcp_packet)
        # Log *after* receiving
        self._log_step("MCP Response (create_form)", response)
        return response
    
    def _handle_add_question(self, params):
        """
        Handle adding a question to a form by sending MCP packet.
        
        Args:
            params: Parameters for question addition
            
        Returns:
            dict: Result of the question addition
        """
        self.logger.info(f"Adding question with params: {params}")
        
        # Prepare MCP packet
        mcp_packet = {
            "tool_name": "add_question",
            "parameters": {
                "form_id": params.get("form_id"),
                "question_type": params.get("type", "text"),
                "title": params.get("title", "Question"),
                "options": params.get("options", []),
                "required": params.get("required", False)
            }
        }
        
        # Log *before* sending
        self._log_step("MCP Request (add_question)", mcp_packet)
        response = self._send_to_mcp_server(mcp_packet)
        # Log *after* receiving
        self._log_step("MCP Response (add_question)", response)
        return response
    
    def _handle_get_responses(self, params):
        """
        Handle getting form responses by sending MCP packet.
        
        Args:
            params: Parameters for getting responses
            
        Returns:
            dict: Form responses
        """
        self.logger.info(f"Getting responses with params: {params}")
        
        # Prepare MCP packet
        mcp_packet = {
            "tool_name": "get_responses",
            "parameters": {
                "form_id": params.get("form_id")
            }
        }
        
        # Log *before* sending
        self._log_step("MCP Request (get_responses)", mcp_packet)
        response = self._send_to_mcp_server(mcp_packet)
        # Log *after* receiving
        self._log_step("MCP Response (get_responses)", response)
        return response
    
    def _send_to_mcp_server(self, mcp_packet):
        """
        Sends an MCP packet to the MCP server URL.
        
        Args:
            mcp_packet: The MCP packet (dict) to send.
            
        Returns:
            dict: The response JSON from the MCP server.
        """
        self.logger.info(f"Sending MCP packet: {json.dumps(mcp_packet)}")
        
        try:
            response = requests.post(
                MCP_SERVER_URL,
                json=mcp_packet,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Add a timeout (e.g., 30 seconds)
            )
            
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.info(f"Received MCP response: {json.dumps(response_data)}")
            return response_data
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout sending MCP packet to {MCP_SERVER_URL}")
            return {"status": "error", "message": "MCP server request timed out"}
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending MCP packet to {MCP_SERVER_URL}: {str(e)}")
            # Try to get error details from response body if possible
            error_detail = str(e)
            try:
                error_detail = e.response.text if e.response else str(e)
            except Exception:
                pass # Ignore errors parsing the error response itself
            return {"status": "error", "message": f"MCP server communication error: {error_detail}"}
        except json.JSONDecodeError as e:
             self.logger.error(f"Error decoding MCP response JSON: {str(e)}")
             return {"status": "error", "message": "Invalid JSON response from MCP server"}
        except Exception as e:
            self.logger.error(f"Unexpected error in _send_to_mcp_server: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"Unexpected agent error sending MCP packet: {str(e)}"}


# For testing
if __name__ == "__main__":
    agent = FormAgent()
    
    # Test with some sample requests
    test_requests = [
        "Create a customer feedback form with a rating question",
        "Make a survey about remote work preferences",
        "Set up an RSVP form for my event on Saturday"
    ]
    
    for req in test_requests:
        print(f"\nProcessing: {req}")
        result = agent.process_request(req)
        print(f"Result: {json.dumps(result, indent=2)}")
