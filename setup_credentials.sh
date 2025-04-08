#!/bin/bash

# Google Forms MCP Server Credentials Setup Script

echo "================================================"
echo "  Google Forms MCP Server - Credentials Setup"
echo "================================================"
echo ""
echo "This script will help you set up your Google API credentials."
echo "You'll need to provide your Client ID, Client Secret, and Refresh Token."
echo ""
echo "If you don't have these credentials yet, please follow the instructions in README.md"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    read -p ".env file already exists. Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

# Get credentials
read -p "Enter your Google Client ID: " client_id
read -p "Enter your Google Client Secret: " client_secret
read -p "Enter your Google Refresh Token: " refresh_token

# Get port settings
read -p "Enter port for MCP Server [5000]: " port
port=${port:-5000}

# Get debug setting
read -p "Enable debug mode? (y/n) [y]: " debug_mode
debug_mode=${debug_mode:-y}

if [ "$debug_mode" == "y" ]; then
    debug="True"
else
    debug="False"
fi

# Create .env file
cat > .env << EOF
# Google API Credentials
GOOGLE_CLIENT_ID=$client_id
GOOGLE_CLIENT_SECRET=$client_secret
GOOGLE_REFRESH_TOKEN=$refresh_token

# Server Configuration
FLASK_ENV=development
PORT=$port
DEBUG=$debug

# CamelAIOrg Agents Configuration
AGENT_ENDPOINT=http://agents:5001/process
AGENT_API_KEY=demo_key
EOF

echo ""
echo "Credentials saved to .env file."
echo ""
echo "You can now start the project with:"
echo "./start.sh"
echo ""
echo "If you need to update your credentials later, you can run this script again"
echo "or edit the .env file directly." 