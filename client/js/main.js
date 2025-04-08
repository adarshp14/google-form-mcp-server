/**
 * Google Forms MCP Client
 * Main JavaScript file for handling server connection and UI updates
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const connectButton = document.getElementById('connectButton');
    const loadingMessage = document.getElementById('loadingMessage');
    const errorMessage = document.getElementById('errorMessage');
    const serverStatusElement = document.getElementById('serverStatus');
    
    // Server configuration
    const config = {
        mcpServerUrl: 'http://localhost:5005',
        agentServerUrl: 'http://localhost:5006'
    };
    
    // Initialize
    function init() {
        // Add event listeners
        if (connectButton) {
            connectButton.addEventListener('click', handleServerConnect);
        }
        
        // Check server status
        checkServerStatus();
    }
    
    // Check if MCP server is available
    async function checkServerStatus() {
        if (serverStatusElement) {
            serverStatusElement.textContent = 'Checking...';
            serverStatusElement.className = 'checking';
        }
        
        try {
            const response = await fetch(`${config.mcpServerUrl}/api/health`);
            
            if (response.ok) {
                const data = await response.json();
                if (serverStatusElement) {
                    serverStatusElement.textContent = `Online (v${data.version})`;
                    serverStatusElement.className = 'online';
                }
                return true;
            } else {
                if (serverStatusElement) {
                    serverStatusElement.textContent = 'Error';
                    serverStatusElement.className = 'offline';
                }
                return false;
            }
        } catch (error) {
            console.error('Server status check error:', error);
            if (serverStatusElement) {
                serverStatusElement.textContent = 'Offline';
                serverStatusElement.className = 'offline';
            }
            return false;
        }
    }
    
    // Handle server connection button click
    function handleServerConnect(e) {
        if (e) {
            e.preventDefault();
        }
        
        if (loadingMessage) {
            loadingMessage.style.display = 'block';
        }
        
        if (errorMessage) {
            errorMessage.style.display = 'none';
        }
        
        // Attempt to connect to the server
        fetch(`${config.mcpServerUrl}/api/health`)
            .then(response => {
                if (response.ok) {
                    window.location.href = config.mcpServerUrl;
                } else {
                    throw new Error('Server error');
                }
            })
            .catch(error => {
                console.error('Connection error:', error);
                if (loadingMessage) {
                    loadingMessage.style.display = 'none';
                }
                
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                }
            });
    }
    
    // Start the application
    init();
});
