#!/bin/bash

# Setup the project with provided credentials

echo "================================================"
echo "  Google Forms MCP Server - Quick Start"
echo "================================================"
echo ""
echo "This script will set up the project with provided credentials"
echo "and start the services."
echo ""

# Create .env file with provided credentials
cat > .env << EOF
# Google API Credentials
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_here

# Server Configuration
FLASK_ENV=development
PORT=5000
DEBUG=True

# CamelAIOrg Agents Configuration
AGENT_ENDPOINT=http://agents:5001/process
AGENT_API_KEY=demo_key
EOF

echo "Created .env file with placeholder credentials."
echo ""
echo "IMPORTANT: You need to edit the .env file with your actual Google API credentials."
echo "You can do this now by running:"
echo "  nano .env"
echo ""
echo "After updating your credentials, start the project with:"
echo "  ./start.sh"
echo ""
echo "Would you like to edit the .env file now? (y/n)"
read edit_now

if [ "$edit_now" == "y" ]; then
    ${EDITOR:-nano} .env
    
    echo ""
    echo "Now that you've updated your credentials, would you like to start the project? (y/n)"
    read start_now
    
    if [ "$start_now" == "y" ]; then
        ./start.sh
    else
        echo "You can start the project later by running ./start.sh"
    fi
else
    echo "Remember to update your credentials in .env before starting the project."
fi 