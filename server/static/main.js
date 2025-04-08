/**
 * Main JavaScript for Google Forms MCP Server UI
 * Handles UI interactions, API calls, and visualization updates
 */

// DOM Elements
const elements = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    requestInput: document.getElementById('requestInput'),
    sendRequestBtn: document.getElementById('sendRequestBtn'),
    demoBtns: document.querySelectorAll('.demo-btn'),
    formResult: document.getElementById('formResult'),
    formTitle: document.getElementById('formTitle'),
    formViewLink: document.getElementById('formViewLink'),
    formEditLink: document.getElementById('formEditLink'),
    questionsList: document.getElementById('questionsList'),
    packetLog: document.getElementById('packetLog')
};

// Templates
const templates = {
    packetEntry: document.getElementById('packetTemplate')
};

// API endpoints
const API = {
    process: '/api/process',
    schema: '/api/schema',
    health: '/api/health',
    agent_proxy: '/api/agent_proxy'
};

// State
let state = {
    connected: false,
    currentForm: null,
    currentTransaction: null,
    questions: []
};

/**
 * Initialize the application
 */
function init() {
    // Set up event listeners
    setupEventListeners();
    
    // Check server connection
    checkServerConnection();
    
    // Show connection status
    updateConnectionStatus(false, 'Connecting...');
    
    console.log('Google Forms MCP Server UI initialized');
}

/**
 * Set up event listeners for UI elements
 */
function setupEventListeners() {
    // Send request button
    elements.sendRequestBtn.addEventListener('click', handleSendRequest);
    
    // Demo buttons
    elements.demoBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const request = this.getAttribute('data-request');
            elements.requestInput.value = request;
            handleSendRequest();
        });
    });
}

/**
 * Check server connection status
 */
async function checkServerConnection() {
    try {
        const response = await fetch(API.health);
        if (response.ok) {
            const data = await response.json();
            updateConnectionStatus(true, `Connected (v${data.version})`);
        } else {
            updateConnectionStatus(false, 'Connection Error');
        }
    } catch (error) {
        console.error('Server connection error:', error);
        updateConnectionStatus(false, 'Connection Error');
    }
}

/**
 * Update connection status indicator
 * @param {boolean} isConnected - Whether the server is connected
 * @param {string} statusMessage - Status message to display
 */
function updateConnectionStatus(isConnected, statusMessage) {
    state.connected = isConnected;
    
    elements.statusDot.className = 'status-dot ' + (isConnected ? 'connected' : 'error');
    elements.statusText.textContent = statusMessage;
    
    elements.sendRequestBtn.disabled = !isConnected;
}

/**
 * Handle sending a request to the agent
 */
async function handleSendRequest() {
    const requestText = elements.requestInput.value.trim(); // Get raw text
    if (!requestText) {
        alert('Please enter a request');
        return;
    }
    
    if (!state.connected) {
        alert('Server is not connected');
        return;
    }
    
    // Clear previous results
    resetResults();
    
    try {
        elements.sendRequestBtn.disabled = true;
        elements.sendRequestBtn.textContent = 'Processing...';
        
        // Log the natural language request
        logPacket({
            transaction_id: 'user-request',
            request: requestText
        }, 'User Request');
        
        // Animation: Frontend -> Agent
        await window.flowAnimator.animateFlow('frontend', 'agent', 'outgoing');

        // Send the raw text request to the Agent server
        const agentResponse = await processWithAgent(requestText);

        // --- Agent processing and MCP calls happen on the backend --- 
        // --- The agentResponse should contain the final result --- 

        // Log the agent's process steps if returned
        if (agentResponse.log_entries && Array.isArray(agentResponse.log_entries)){
             logAgentSteps(agentResponse.log_entries);
        }

        // Animation: Agent -> Frontend (assuming agent handles intermediate steps)
        await window.flowAnimator.animateFlow('agent', 'frontend', 'incoming');

        // Check agent response status
        if (agentResponse.status === 'success' && agentResponse.result) {
             // Assuming the agent returns the final form details in agentResponse.result.final_form
             // Or potentially just the success message and logs the details server-side.
             // Let's adapt based on what the agent will return.
             // For now, let's assume it returns the created form details directly.
            if (agentResponse.result.form_id) { 
                // Log the final successful response from the agent/MCP flow
                logPacket(agentResponse, 'Final Response');
                // Update the UI with the final form details
                // We need to determine what structure the agent will return.
                // Let's assume it returns the standard form result structure.
                // We might need to adjust getQuestionsFromRequest or have the agent return questions.
                updateFormResult(agentResponse.result, agentResponse.result.questions || []); 
            } else {
                 logPacket(agentResponse, 'Agent Response (No Form)');
                 alert('Agent processed the request, but no form details were returned.');
            }
        } else {
            // Log the error response from the agent
            logPacket(agentResponse, 'Agent Error');
            throw new Error(agentResponse.message || 'Agent processing failed');
        }
        
    } catch (error) {
        console.error('Error during form creation process:', error);
        alert(`An error occurred: ${error.message}`);
        // Log error packet if possible
         logPacket({ error: error.message }, 'Processing Error');
    } finally {
        elements.sendRequestBtn.disabled = false;
        elements.sendRequestBtn.textContent = 'Send Request';
        // Reset animations or UI states if needed
        window.flowAnimator.resetAll(); 
    }
}

/**
 * Sends the natural language request to the agent server.
 * @param {string} requestText - The raw natural language text.
 * @returns {Promise<Object>} - The response from the agent server.
 */
async function processWithAgent(requestText) {
    console.log(`Sending request via proxy to agent: ${requestText}`); // Debug log
    try {
        const response = await fetch(API.agent_proxy, { // Use the PROXY endpoint
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ request_text: requestText })
        });

        // Log raw response status
        console.log(`Agent response status: ${response.status}`);

        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { message: await response.text() || 'Failed to parse error response' };
            }
            console.error('Agent API Error:', response.status, errorData);
            // Try to construct a meaningful error message
            let errorMsg = `Agent request failed: ${response.status} ${response.statusText || ''}`;
            if (errorData && errorData.message) {
                errorMsg += ` - ${errorData.message}`;
            }
            throw new Error(errorMsg);
        }
        
        const responseData = await response.json();
        console.log('Agent response data:', responseData); // Debug log
        return responseData;

    } catch (error) {
        console.error('Error sending request to agent:', error);
        // Return a structured error object for the UI handler
        return { 
            status: 'error', 
            message: error.message || 'Failed to communicate with agent server'
        };
    }
}

/**
 * Create an MCP packet for a tool call
 * @param {string} toolName - Name of the MCP tool to call
 * @param {Object} parameters - Parameters for the tool
 * @returns {Object} - Formatted MCP packet
 */
function createMCPPacket(toolName, parameters) {
    return {
        transaction_id: 'tx_' + Math.random().toString(36).substr(2, 9),
        tool_name: toolName,
        parameters: parameters
    };
}

/**
 * Log an MCP packet or Agent Step to the UI
 * @param {Object} item - The packet or log entry object
 * @param {string} type - 'MCP Request', 'MCP Response', 'Agent Step', etc.
 */
function logItem(item, type) {
    // Clone the template
    const template = templates.packetEntry.content.cloneNode(true);
    
    // Set the data
    template.querySelector('.transaction-id').textContent = item.transaction_id || item.step_type || 'N/A';
    template.querySelector('.packet-time').textContent = item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    
    const directionEl = template.querySelector('.packet-direction');
    directionEl.textContent = type;
    
    // Add specific classes for styling
    if (type.includes('Request')) {
        directionEl.classList.add('request');
    } else if (type.includes('Response')) {
        directionEl.classList.add('response');
    } else if (type.includes('Agent')) {
         directionEl.classList.add('agent-step'); // Add a class for agent steps
    } else if (type.includes('User')) {
         directionEl.classList.add('user-request');
    } else if (type.includes('Error')) {
         directionEl.classList.add('error-log');
    }
    
    // Format the content (use item.data for agent steps)
    const contentToDisplay = type === 'Agent Step' ? item.data : item;
    template.querySelector('.packet-content').textContent = JSON.stringify(contentToDisplay, null, 2);
    
    // Add to the log
    elements.packetLog.prepend(template);
}

/**
 * Logs agent processing steps provided by the backend.
 * @param {Array<Object>} logEntries - Array of log entry objects from the agent.
 */
function logAgentSteps(logEntries) {
    // Log entries in reverse order so newest appear first in the UI log
    // Or log them sequentially as they happened?
    // Let's log sequentially as they happened for chronological understanding.
    logEntries.forEach(entry => {
        logItem(entry, 'Agent Step');
    });
}

/**
 * Modify the old logPacket function to use logItem
 */
function logPacket(packet, direction) {
    logItem(packet, direction);
}

/**
 * Reset the results UI
 */
function resetResults() {
    elements.formResult.classList.add('hidden');
    elements.questionsList.innerHTML = '';
    state.currentForm = null;
    state.currentTransaction = null;
    state.questions = [];
}

/**
 * Update the form result UI
 * @param {Object} formData - Form data from the API
 * @param {Array} questions - Questions to display
 */
function updateFormResult(formData, questions) {
    state.currentForm = formData;
    
    elements.formTitle.textContent = formData.title;
    elements.formViewLink.href = formData.response_url;
    elements.formEditLink.href = formData.edit_url;
    
    // Add questions to the list
    elements.questionsList.innerHTML = '';
    questions.forEach(question => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        
        let questionText = `<strong>${question.title}</strong><br>`;
        questionText += `Type: ${question.type}`;
        
        if (question.options && question.options.length > 0) {
            questionText += `<br>Options: ${question.options.join(', ')}`;
        }
        
        li.innerHTML = questionText;
        elements.questionsList.appendChild(li);
    });
    
    // Show the form result
    elements.formResult.classList.remove('hidden');
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
