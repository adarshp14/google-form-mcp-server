#!/bin/bash

# Display welcome message
echo "================================================"
echo "  Google Forms MCP Server with CamelAIOrg Agents"
echo "================================================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with your Google API credentials."
    echo "Example format:"
    echo "GOOGLE_CLIENT_ID=your_client_id"
    echo "GOOGLE_CLIENT_SECRET=your_client_secret"
    echo "GOOGLE_REFRESH_TOKEN=your_refresh_token"
    echo ""
    echo "PORT=5000"
    echo "DEBUG=True"
    echo ""
    exit 1
fi

# Build and start containers
echo "Starting services with Docker Compose..."
docker-compose up --build -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Display service status
echo ""
echo "Service Status:"
docker-compose ps

# Display access information
echo ""
echo "Access Information:"
echo "- MCP Server: http://localhost:5005"
echo "- Agent Server: http://localhost:5006"
echo "- Client Interface: Open client/index.html in your browser"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the services:"
echo "  docker-compose down"
echo ""
echo "Enjoy using the Google Forms MCP Server!" 