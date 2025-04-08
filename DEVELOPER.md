# Google Forms MCP Server - Developer Guide

This document provides technical details for developers who want to understand, modify, or extend the Google Forms MCP Server and CamelAIOrg Agents integration.

## Architecture Overview

The system is built on a modular architecture with the following key components:

1. **MCP Server (Flask)**: Implements the Model Context Protocol and interfaces with Google Forms API
2. **CamelAIOrg Agents (Flask)**: Processes natural language and converts it to structured MCP calls
3. **Frontend UI (HTML/CSS/JS)**: Visualizes the flow and manages user interactions
4. **Google Forms API**: External service for form creation and management

### Component Communication

```
Frontend → Agents → MCP Server → Google Forms API
```

Each component communicates via HTTP requests, with MCP packets being the primary data format for the MCP Server.

## MCP Protocol Specification

The MCP (Model Context Protocol) is designed to standardize tool usage between AI agents and external services. Our implementation follows these guidelines:

### Request Format

```json
{
  "transaction_id": "unique_id",
  "tool_name": "tool_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format

```json
{
  "transaction_id": "unique_id",
  "status": "success|error",
  "result": {
    "key1": "value1",
    "key2": "value2"
  },
  "error": {
    "message": "Error message"
  }
}
```

## Google Forms API Integration

The integration with Google Forms API is handled by the `GoogleFormsAPI` class in `forms_api.py`. Key methods include:

- `create_form(title, description)`: Creates a new form
- `add_question(form_id, question_type, title, options, required)`: Adds a question
- `get_responses(form_id)`: Retrieves form responses

### Authentication Flow

1. OAuth2 credentials are stored in environment variables
2. Credentials are loaded and used to create a Google API client
3. API requests are authenticated using these credentials

## CamelAIOrg Agent Implementation

The agent implementation in `agent_integration.py` provides the natural language processing interface. Key methods:

- `process_request(request_text)`: Main entry point for NL requests
- `_analyze_request(request_text)`: Analyzes and extracts intent from text
- `_handle_create_form(params)`: Creates a form based on extracted parameters

## Frontend Visualization

The UI uses a combination of CSS and JavaScript to visualize the request flow:

- **Flow Lines**: Represent the path between components
- **Particles**: Animated elements that travel along flow lines
- **Nodes**: Represent each component (Frontend, Agents, MCP, Google)
- **MCP Packet Log**: Shows the actual MCP packets being exchanged

### Animation System

The animation system in `animations.js` provides these key features:

- `animateFlow(fromNode, toNode, direction)`: Animates flow between nodes
- `animateRequestResponseFlow()`: Animates a complete request-response cycle
- `animateErrorFlow(errorStage)`: Visualizes errors at different stages

## Extending the System

### Adding New Question Types

To add a new question type:

1. Update the `add_question` method in `forms_api.py`
2. Add the new type to the validation in `_handle_add_question` in `mcp_handler.py`
3. Update the UI logic in `main.js` to handle the new question type

### Adding New MCP Tools

To add a new MCP tool:

1. Add the tool name to `MCP_TOOLS` in `config.py`
2. Add tool schema to `get_tools_schema` in `mcp_handler.py`
3. Create a handler method `_handle_tool_name` in `mcp_handler.py`
4. Implement the underlying functionality in `forms_api.py`

### Enhancing Agent Capabilities

To improve the agent's language processing:

1. Enhance the `_analyze_request` method in `agent_integration.py`
2. Add new intents and parameters recognition
3. Adjust the question generation logic based on request analysis

## Testing

### Unit Testing

Test individual components:

```bash
# Test MCP handler
python -m unittest tests/test_mcp_handler.py

# Test Google Forms API
python -m unittest tests/test_forms_api.py

# Test agent integration
python -m unittest tests/test_agent_integration.py
```

### Integration Testing

Test the entire system:

```bash
# Start the servers
docker-compose up -d

# Run integration tests
python -m unittest tests/test_integration.py
```

## Performance Considerations

- **Caching**: Implement caching for frequently accessed forms data
- **Rate Limiting**: Be aware of Google Forms API rate limits
- **Error Handling**: Implement robust error handling and retry logic
- **Load Testing**: Use tools like Locust to test system performance

## Security Best Practices

- **Credential Management**: Never commit credentials to version control
- **Input Validation**: Validate all user input and MCP packets
- **CORS Configuration**: Configure CORS appropriately for production
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Auth Tokens**: Use proper authentication for production deployments

## Deployment

### Production Deployment

For production deployment:

1. Use a proper container orchestration system (Kubernetes, ECS)
2. Set up a reverse proxy (Nginx, Traefik) for TLS termination
3. Use a managed database for persistent data
4. Implement proper monitoring and logging
5. Set up CI/CD pipelines for automated testing and deployment

### Environment-Specific Configuration

Create environment-specific configuration:

- `config.dev.py` - Development settings
- `config.test.py` - Testing settings
- `config.prod.py` - Production settings

## Troubleshooting

Common issues and solutions:

1. **Google API Authentication Errors**:
   - Verify credentials in `.env` file
   - Check that required API scopes are included
   - Ensure refresh token is valid

2. **Docker Network Issues**:
   - Make sure services can communicate on the network
   - Check port mappings in `docker-compose.yml`

3. **UI Animation Issues**:
   - Check browser console for JavaScript errors
   - Verify DOM element IDs match expected values

4. **MCP Protocol Errors**:
   - Validate request format against MCP schema
   - Check transaction IDs are being properly passed

## Contributing

Please follow these guidelines when contributing:

1. Create a feature branch from `main`
2. Follow the existing code style and conventions
3. Write unit tests for new functionality
4. Document new features or changes
5. Submit a pull request with a clear description of changes 