# Quick Start Guide

Follow these steps to get the Google Forms MCP Server up and running quickly.

## Prerequisites

- Docker and Docker Compose installed
- Google account with access to Google Forms
- Google Cloud Platform project with Forms API enabled

## Setup in 5 Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/google-form-mcp-server.git
cd google-form-mcp-server
```

### 2. Get Google API Credentials

If you already have your credentials, proceed to step 3. Otherwise:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Forms API and Google Drive API
3. Create OAuth 2.0 credentials (Web application type)
4. Use the OAuth 2.0 Playground to get a refresh token:
   - Go to: https://developers.google.com/oauthplayground/
   - Configure with your credentials (⚙️ icon)
   - Select Forms and Drive API scopes
   - Authorize and exchange for tokens

### 3. Run the Credentials Setup Script

```bash
./setup_credentials.sh
```

Enter your Google API credentials when prompted.

### 4. Start the Services

```bash
./start.sh
```

This will build and start the Docker containers for the MCP Server and CamelAIOrg Agents.

### 5. Access the Application

Open your browser and navigate to:

- Server UI: http://localhost:5005
- Manual client: Open `client/index.html` in your browser

## Using the Application

1. Enter natural language instructions like:
   - "Create a customer feedback form with a rating question"
   - "Create a survey about remote work preferences"
   - "Make an RSVP form for my event"

2. Watch the request flow through the system visualization

3. View the generated form details and links

## Troubleshooting

- **Server not starting**: Check Docker is running and ports 5005/5006 are available
- **Authentication errors**: Verify your credentials in the .env file
- **Connection errors**: Ensure your network allows API calls to Google

## What's Next?

- Read the full README.md for detailed information
- Check DEVELOPER.md for technical documentation
- Explore the codebase to understand the implementation

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Forms MCP Client</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="container">
        <h1>Google Forms MCP Client</h1>
        <p>This client connects to the Google Forms MCP Server and CamelAIOrg Agents to create forms using natural language.</p>
        
        <div class="server-status">
            <h2>Server Status</h2>
            <p>MCP Server: <span id="serverStatus">Unknown</span></p>
        </div>
        
        <a href="http://localhost:5005" class="button pulse" id="connectButton">Connect to Server</a>
        
        <div class="status loading" id="loadingMessage">
            Connecting to server...
        </div>
        
        <div class="status error" id="errorMessage">
            Could not connect to the server. Please make sure the MCP server is running.
        </div>
        
        <div class="features">
            <h2>Features</h2>
            <ul>
                <li>Create Google Forms with natural language</li>
                <li>Multiple question types support</li>
                <li>View form creation process in real-time</li>
                <li>Monitor API requests and responses</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Google Forms MCP Server with CamelAIOrg Agents Integration</p>
        </div>
    </div>
    
    <script src="js/main.js"></script>
</body>
</html> 