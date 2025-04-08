/**
 * Flow Animation Module for Google Forms MCP Server
 * Manages the visual animations of data flowing between components
 */

class FlowAnimator {
    constructor() {
        // Flow nodes
        this.nodes = {
            frontend: document.getElementById('frontendNode'),
            agent: document.getElementById('agentNode'),
            mcp: document.getElementById('mcpNode'),
            google: document.getElementById('googleNode')
        };
        
        // Flow lines
        this.lines = {
            frontendToAgent: document.getElementById('frontendToAgent'),
            agentToMCP: document.getElementById('agentToMCP'),
            mcpToGoogle: document.getElementById('mcpToGoogle')
        };
        
        // Particle colors
        this.colors = {
            outgoing: '#00ccff', // Cyan for outgoing requests
            incoming: '#00ff9d', // Green for incoming responses
            error: '#ff4757'     // Red for errors
        };
        
        // Animation state
        this.activeAnimations = [];
        this.isAnimating = false;
        this.currentActiveNode = null;
        this.currentActiveLine = null;
        
        // Animation intervals for continuous particle generation
        this.particleIntervals = {};
    }
    
    /**
     * Activate a node with a glowing effect
     * @param {string} nodeName - The name of the node to activate
     */
    activateNode(nodeName) {
        if (this.nodes[nodeName]) {
            // Deactivate previous node if exists
            if (this.currentActiveNode && this.nodes[this.currentActiveNode]) {
                this.nodes[this.currentActiveNode].classList.remove('active');
            }
            
            // Add active class to the node
            this.nodes[nodeName].classList.add('active');
            this.currentActiveNode = nodeName;
            
            // Return a cleanup function
            return () => {
                // Only remove active class if this is still the current active node
                if (this.currentActiveNode === nodeName) {
                    this.nodes[nodeName].classList.remove('active');
                    this.currentActiveNode = null;
                }
            };
        }
        return () => {};
    }
    
    /**
     * Activate a flow line
     * @param {string} lineName - The name of the line to activate
     */
    activateLine(lineName) {
        if (this.lines[lineName]) {
            // Deactivate previous line if exists
            if (this.currentActiveLine && this.lines[this.currentActiveLine]) {
                this.lines[this.currentActiveLine].classList.remove('active');
            }
            
            // Add active class to the line
            this.lines[lineName].classList.add('active');
            this.currentActiveLine = lineName;
            
            // Return a cleanup function
            return () => {
                // Only remove active class if this is still the current active line
                if (this.currentActiveLine === lineName) {
                    this.lines[lineName].classList.remove('active');
                    this.currentActiveLine = null;
                }
            };
        }
        return () => {};
    }
    
    /**
     * Create and animate a particle flowing through a line
     * @param {string} lineName - The name of the line to animate
     * @param {string} direction - 'outgoing' or 'incoming' to determine color and direction
     * @param {number} duration - Animation duration in milliseconds
     */
    createParticle(lineName, direction, duration = 800) {
        const line = this.lines[lineName];
        if (!line) return null;
        
        const container = line.querySelector('.flow-particle-container');
        if (!container) return null;
        
        // Create particle element
        const particle = document.createElement('div');
        particle.className = 'flow-particle';
        particle.style.position = 'absolute';
        particle.style.width = '7px';
        particle.style.height = '7px';
        particle.style.borderRadius = '50%';
        particle.style.backgroundColor = this.colors[direction] || this.colors.outgoing;
        particle.style.boxShadow = `0 0 8px 2px ${this.colors[direction] || this.colors.outgoing}`;
        
        // Set starting position based on direction
        if (direction === 'incoming') {
            particle.style.top = 'calc(100% - 7px)';
            particle.style.transform = 'translateY(0)';
        } else {
            particle.style.top = '0';
            particle.style.transform = 'translateY(0)';
        }
        
        // Add particle to container
        container.appendChild(particle);
        
        // Animate the particle
        const animation = particle.animate([
            { 
                top: direction === 'incoming' ? 'calc(100% - 7px)' : '0',
                opacity: 1 
            },
            { 
                top: direction === 'incoming' ? '0' : 'calc(100% - 7px)',
                opacity: 0.8 
            }
        ], {
            duration: duration,
            easing: 'ease-out',
            fill: 'forwards'
        });
        
        // Remove particle when animation completes
        animation.onfinish = () => {
            if (container.contains(particle)) {
                container.removeChild(particle);
            }
        };
        
        return animation;
    }
    
    /**
     * Start continuous particle animation on a line
     * @param {string} lineName - The line to animate
     * @param {string} direction - Direction of flow
     */
    startContinuousParticles(lineName, direction) {
        // Clear any existing interval for this line
        this.stopContinuousParticles(lineName);
        
        // Create new interval
        const interval = setInterval(() => {
            this.createParticle(lineName, direction, 800);
        }, 200);
        
        // Store the interval
        this.particleIntervals[lineName] = interval;
    }
    
    /**
     * Stop continuous particle animation on a line
     * @param {string} lineName - The line to stop animating
     */
    stopContinuousParticles(lineName) {
        if (this.particleIntervals[lineName]) {
            clearInterval(this.particleIntervals[lineName]);
            delete this.particleIntervals[lineName];
            
            // Clear any remaining particles
            const line = this.lines[lineName];
            if (line) {
                const container = line.querySelector('.flow-particle-container');
                if (container) {
                    container.innerHTML = '';
                }
            }
        }
    }
    
    /**
     * Stop all continuous particle animations
     */
    stopAllContinuousParticles() {
        Object.keys(this.particleIntervals).forEach(lineName => {
            this.stopContinuousParticles(lineName);
        });
    }
    
    /**
     * Animate flow from one node to another
     * @param {string} fromNode - Source node name
     * @param {string} toNode - Target node name
     * @param {string} direction - 'outgoing' or 'incoming'
     * @returns {Promise} - Resolves when animation completes
     */
    async animateFlow(fromNode, toNode, direction = 'outgoing') {
        // Define flow paths
        const flowPaths = {
            'frontend-agent': 'frontendToAgent',
            'agent-mcp': 'agentToMCP',
            'mcp-google': 'mcpToGoogle',
            'google-mcp': 'mcpToGoogle',
            'mcp-agent': 'agentToMCP',
            'agent-frontend': 'frontendToAgent'
        };
        
        const pathKey = `${fromNode}-${toNode}`;
        const lineName = flowPaths[pathKey];
        
        if (!lineName) {
            console.error(`No flow path defined for ${pathKey}`);
            return;
        }
        
        // Stop any existing continuous animations
        this.stopAllContinuousParticles();
        
        // Activate source node
        const cleanupSource = this.activateNode(fromNode);
        
        // Activate the flow line
        const cleanupLine = this.activateLine(lineName);
        
        // Start continuous particles
        this.startContinuousParticles(lineName, direction);
        
        // Create promise that resolves when animation completes
        return new Promise(resolve => {
            setTimeout(() => {
                // Activate target node
                const cleanupTarget = this.activateNode(toNode);
                
                // Stop continuous particles
                this.stopContinuousParticles(lineName);
                
                // Cleanup source node after delay
                cleanupSource();
                
                // Cleanup line
                cleanupLine();
                
                // Resolve the promise
                resolve();
            }, 1500); // Longer wait to show the flow more clearly
        });
    }
    
    /**
     * Animate a complete request-response flow
     * @param {string} scenario - The flow scenario to animate
     */
    async animateRequestResponseFlow(scenario = 'form-creation') {
        // Prevent multiple animations
        if (this.isAnimating) return;
        this.isAnimating = true;
        
        try {
            // Common flow for all scenarios
            // Frontend -> Agent -> MCP -> Google -> MCP -> Agent -> Frontend
            
            // Request flow
            await this.animateFlow('frontend', 'agent', 'outgoing');
            await this.animateFlow('agent', 'mcp', 'outgoing');
            await this.animateFlow('mcp', 'google', 'outgoing');
            
            // Response flow
            await this.animateFlow('google', 'mcp', 'incoming');
            await this.animateFlow('mcp', 'agent', 'incoming');
            await this.animateFlow('agent', 'frontend', 'incoming');
            
        } catch (error) {
            console.error('Animation error:', error);
        } finally {
            this.isAnimating = false;
        }
    }
    
    /**
     * Animate a flow with an error
     * @param {string} errorStage - The stage where the error occurs
     */
    async animateErrorFlow(errorStage = 'google') {
        if (this.isAnimating) return;
        this.isAnimating = true;
        
        try {
            // Initial flow
            await this.animateFlow('frontend', 'agent', 'outgoing');
            
            if (errorStage === 'agent') {
                // Error at agent
                this.nodes.agent.classList.add('error');
                setTimeout(() => {
                    this.nodes.agent.classList.remove('error');
                    this.nodes.agent.classList.remove('active');
                }, 2000);
                return;
            }
            
            await this.animateFlow('agent', 'mcp', 'outgoing');
            
            if (errorStage === 'mcp') {
                // Error at MCP server
                this.nodes.mcp.classList.add('error');
                setTimeout(() => {
                    this.nodes.mcp.classList.remove('error');
                    this.nodes.mcp.classList.remove('active');
                }, 2000);
                return;
            }
            
            await this.animateFlow('mcp', 'google', 'outgoing');
            
            if (errorStage === 'google') {
                // Error at Google Forms API
                this.nodes.google.classList.add('error');
                setTimeout(() => {
                    this.nodes.google.classList.remove('error');
                    this.nodes.google.classList.remove('active');
                    
                    // Error response flow
                    this.animateFlow('google', 'mcp', 'error');
                    this.animateFlow('mcp', 'agent', 'error');
                    this.animateFlow('agent', 'frontend', 'error');
                }, 2000);
            }
            
        } catch (error) {
            console.error('Error animation error:', error);
        } finally {
            setTimeout(() => {
                this.isAnimating = false;
            }, 3000);
        }
    }
    
    /**
     * Reset all animations and active states
     */
    resetAll() {
        // Stop all continuous particles
        this.stopAllContinuousParticles();
        
        // Reset nodes
        Object.values(this.nodes).forEach(node => {
            node.classList.remove('active');
            node.classList.remove('error');
            node.classList.remove('pulse');
        });
        
        // Reset lines
        Object.values(this.lines).forEach(line => {
            line.classList.remove('active');
            const container = line.querySelector('.flow-particle-container');
            if (container) {
                container.innerHTML = '';
            }
        });
        
        this.currentActiveNode = null;
        this.currentActiveLine = null;
        this.isAnimating = false;
    }
    
    /**
     * Pulse animation for a specific node
     * @param {string} nodeName - Name of the node to pulse
     * @param {number} duration - Duration in milliseconds
     */
    pulseNode(nodeName, duration = 2000) {
        const node = this.nodes[nodeName];
        if (!node) return;
        
        node.classList.add('pulse');
        
        setTimeout(() => {
            node.classList.remove('pulse');
        }, duration);
    }
    
    /**
     * Highlight a specific node to show it's the current active component
     * @param {string} nodeName - Name of the node to highlight
     */
    highlightNode(nodeName) {
        // First clear any existing highlights
        Object.keys(this.nodes).forEach(name => {
            this.nodes[name].classList.remove('highlighted');
        });
        
        // Set the new highlight
        if (this.nodes[nodeName]) {
            this.nodes[nodeName].classList.add('highlighted');
        }
    }
}

// Initialize flow animator when document loads
document.addEventListener('DOMContentLoaded', function() {
    window.flowAnimator = new FlowAnimator();
    
    // For demo purposes, animate the request flow on load to demonstrate functionality
    setTimeout(() => {
        if (window.flowAnimator) {
            window.flowAnimator.animateRequestResponseFlow();
        }
    }, 2000);
});
