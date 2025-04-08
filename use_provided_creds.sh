#!/bin/bash

# Setup the project with user-provided credentials

echo "================================================"
echo "  Google Forms MCP Server - Use Provided Credentials"
echo "================================================"
echo ""

# Check if credentials were provided
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: $0 <client_id> <client_secret> <refresh_token>"
    echo ""
    echo "Example:"
    echo "$0 123456789-abcdef.apps.googleusercontent.com GOCSPX-abc123def456 1//04abcdefghijklmnop"
    exit 1
fi

# Get credentials from arguments
CLIENT_ID=$1
CLIENT_SECRET=$2
REFRESH_TOKEN=$3

# Create .env file with provided credentials
cat > .env << EOF
# Google API Credentials
GOOGLE_CLIENT_ID=$CLIENT_ID
GOOGLE_CLIENT_SECRET=$CLIENT_SECRET
GOOGLE_REFRESH_TOKEN=$REFRESH_TOKEN

# Server Configuration
FLASK_ENV=development
PORT=5000
DEBUG=True

# CamelAIOrg Agents Configuration
AGENT_ENDPOINT=http://agents:5001/process
AGENT_API_KEY=demo_key
EOF

echo "Created .env file with your provided credentials."
echo ""
echo "Starting the project now..."
echo ""

# Start the project
./start.sh 