/**
 * Google Forms MCP Server
 * Main JavaScript file for handling server interactions, UI updates, and flow visualization
 */

// State management
const state = {
    isConnected: false,
    currentForm: null,
    currentTransaction: null,
    requestInProgress: false,
    currentStage: null, // Tracks the current stage in the flow
    questions: []
};

// Stages in the flow
const STAGES = {
    IDLE: 'idle',
    FRONTEND: 'frontend',
    AGENT: 'agent',
    MCP: 'mcp',
    GOOGLE: 'google',
    COMPLETE: 'complete',
    ERROR: 'error'
};

// API endpoints
const API = {
    health: '/api/health',
    form_request: '/api/form_request',
    agent_proxy: '/api/agent_proxy',
    form_status: '/api/form_status'
};

// DOM Elements
const elements = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    requestInput: document.getElementById('requestInput'),
    sendRequestBtn: document.getElementById('sendRequestBtn'),
    formResult: document.getElementById('formResult'),
    formTitle: document.getElementById('formTitle'),
    formViewLink: document.getElementById('formViewLink'),
    formEditLink: document.getElementById('formEditLink'),
    questionsList: document.getElementById('questionsList'),
    packetLog: document.getElementById('packetLog'),
    demoBtns: document.querySelectorAll('.demo-btn'),
    stageIndicator: document.getElementById('stageIndicator')
};

// Templates
const templates = {
    packetEntry: document.getElementById('packetTemplate')
};

/**
 * Initialize the application
 */
function init() {
    // Set up event listeners
    setupEventListeners();
    
    // Check server connection
    checkServerConnection();
    
    // Initialize stage
    updateStage(STAGES.IDLE);
    
    // Pulse frontend node on initial load to indicate entry point
    setTimeout(() => {
        if (window.flowAnimator) {
            window.flowAnimator.pulseNode('frontend', 3000);
        }
    }, 1000);
}

/**
 * Update the current stage in the flow
 * @param {string} stage - The current stage
 */
function updateStage(stage) {
    state.currentStage = stage;
    
    // Update visual indication of current stage
    if (window.flowAnimator) {
        // Highlight the appropriate node based on stage
        switch (stage) {
            case STAGES.FRONTEND:
                window.flowAnimator.highlightNode('frontend');
                break;
            case STAGES.AGENT:
                window.flowAnimator.highlightNode('agent');
                break;
            case STAGES.MCP:
                window.flowAnimator.highlightNode('mcp');
                break;
            case STAGES.GOOGLE:
                window.flowAnimator.highlightNode('google');
                break;
            default:
                // Clear highlights for IDLE, COMPLETE, ERROR
                Object.keys(window.flowAnimator.nodes).forEach(nodeName => {
                    window.flowAnimator.nodes[nodeName].classList.remove('highlighted');
                });
                break;
        }
    }
    
    // Update stage indicator text if present
    if (elements.stageIndicator) {
        let stageText = '';
        switch (stage) {
            case STAGES.IDLE:
                stageText = 'Ready for request';
                break;
            case STAGES.FRONTEND:
                stageText = 'Processing in frontend';
                break;
            case STAGES.AGENT:
                stageText = 'Agent processing request';
                break;
            case STAGES.MCP:
                stageText = 'MCP Server building form';
                break;
            case STAGES.GOOGLE:
                stageText = 'Interacting with Google Forms';
                break;
            case STAGES.COMPLETE:
                stageText = 'Form creation complete';
                break;
            case STAGES.ERROR:
                stageText = 'Error occurred';
                break;
            default:
                stageText = 'Processing...';
        }
        elements.stageIndicator.textContent = stageText;
    }
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    if (elements.sendRequestBtn) {
        elements.sendRequestBtn.addEventListener('click', handleSendRequest);
    }
    
    // Demo buttons
    elements.demoBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const requestText = this.getAttribute('data-request');
            if (elements.requestInput && requestText) {
                elements.requestInput.value = requestText;
                // Automatically trigger request after a short delay
                setTimeout(() => {
                    handleSendRequest();
                }, 500);
            }
        });
    });
}

/**
 * Check if server is connected
 */
async function checkServerConnection() {
    try {
        const response = await fetch(API.health);
        if (response.ok) {
            const data = await response.json();
            updateConnectionStatus(true, `Connected (v${data.version})`);
            return true;
        } else {
            updateConnectionStatus(false, 'Server Error');
            return false;
        }
    } catch (error) {
        console.error('Server connection error:', error);
        updateConnectionStatus(false, 'Disconnected');
        return false;
    }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(isConnected, statusMessage) {
    state.isConnected = isConnected;
    
    if (elements.statusDot) {
        elements.statusDot.className = 'status-dot ' + (isConnected ? 'connected' : 'error');
    }
    
    if (elements.statusText) {
        elements.statusText.textContent = statusMessage || (isConnected ? 'Connected' : 'Disconnected');
    }
}

/**
 * Handle the form request submission
 */
async function handleSendRequest() {
    // Validation & state check
    if (!elements.requestInput || !elements.requestInput.value.trim()) {
        alert('Please enter a request');
        return;
    }
    
    if (state.requestInProgress) {
        return;
    }
    
    // Reset any previous results
    resetResults();
    
    // Update UI
    state.requestInProgress = true;
    elements.sendRequestBtn.disabled = true;
    elements.sendRequestBtn.textContent = 'Processing...';
    
    // Get the request text
    const requestText = elements.requestInput.value.trim();
    
    // Log the user request
    logPacket({ request_text: requestText }, 'User Request');
    
    try {
        // Start at frontend
        updateStage(STAGES.FRONTEND);
        
        // Pulse frontend node to start the flow
        window.flowAnimator.pulseNode('frontend', 1000);
        
        // Animate the request flow from frontend to agent
        await window.flowAnimator.animateFlow('frontend', 'agent', 'outgoing');
        
        // Update stage to agent
        updateStage(STAGES.AGENT);
        
        // Process the request with the agent
        const agentResponse = await processWithAgent(requestText);
        
        // Log agent proxy response
        logPacket(agentResponse, 'Agent Processing');
        
        if (agentResponse.status === 'error') {
            // Show error animation in the flow diagram
            window.flowAnimator.animateErrorFlow('agent');
            updateStage(STAGES.ERROR);
            throw new Error(agentResponse.message || 'Agent processing failed');
        }
        
        // Continue flow to MCP server
        await window.flowAnimator.animateFlow('agent', 'mcp', 'outgoing');
        updateStage(STAGES.MCP);
        
        // Simulate MCP server processing time
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Continue flow to Google Forms
        await window.flowAnimator.animateFlow('mcp', 'google', 'outgoing');
        updateStage(STAGES.GOOGLE);
        
        // Simulate Google Forms API interaction time
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Begin response flow
        // From Google back to MCP
        await window.flowAnimator.animateFlow('google', 'mcp', 'incoming');
        updateStage(STAGES.MCP);
        
        // From MCP back to agent
        await window.flowAnimator.animateFlow('mcp', 'agent', 'incoming');
        updateStage(STAGES.AGENT);
        
        // Final response from agent to frontend
        await window.flowAnimator.animateFlow('agent', 'frontend', 'incoming');
        updateStage(STAGES.FRONTEND);
        
        // Check agent response status
        if (agentResponse.status === 'success' && agentResponse.result) {
            if (agentResponse.result.form_id) { 
                // Log the final successful response from the agent/MCP flow
                logPacket(agentResponse, 'Final Response');
                
                // Update the UI with the final form details
                updateFormResult(agentResponse.result, agentResponse.result.questions || []); 
                
                // Update stage to complete
                updateStage(STAGES.COMPLETE);
            } else {
                logPacket(agentResponse, 'Agent Response (No Form)');
                alert('Agent processed the request, but no form details were returned.');
                updateStage(STAGES.ERROR);
            }
        } else {
            // Log the error response from the agent
            logPacket(agentResponse, 'Agent Error');
            
            // Show error animation in the flow diagram
            window.flowAnimator.animateErrorFlow('agent');
            updateStage(STAGES.ERROR);
            
            throw new Error(agentResponse.message || 'Agent processing failed');
        }
        
    } catch (error) {
        console.error('Error during form creation process:', error);
        alert(`An error occurred: ${error.message}`);
        // Log error packet if possible
        logPacket({ error: error.message }, 'Processing Error');
        updateStage(STAGES.ERROR);
    } finally {
        elements.sendRequestBtn.disabled = false;
        elements.sendRequestBtn.textContent = 'Process Request';
        state.requestInProgress = false;
        
        // Reset flow animator if there was an error
        if (state.currentStage === STAGES.ERROR) {
            setTimeout(() => {
                if (window.flowAnimator) {
                    window.flowAnimator.resetAll();
                    updateStage(STAGES.IDLE);
                }
            }, 3000);
        }
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
    
    // Reset animation state
    if (window.flowAnimator) {
        window.flowAnimator.resetAll();
    }
    
    // Reset to idle state
    updateStage(STAGES.IDLE);
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
    
    // Pulse frontend node to indicate completion
    window.flowAnimator.pulseNode('frontend');
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
