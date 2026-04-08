"""HTML template for the chat interface"""


def get_chat_html() -> str:
    """Generate the chat interface HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Stock Chat Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .header h1 {
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            margin-top: 0.25rem;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            padding: 1rem;
            width: 100%;
        }
        
        .chat-messages {
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
            overflow-y: auto;
            max-height: 60vh;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            max-width: 85%;
            word-wrap: break-word;
        }
        
        .message.user {
            background: #007AFF;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: #f1f3f4;
            color: #333;
            border: 1px solid #e0e0e0;
        }
        
        .message-time {
            font-size: 0.75rem;
            opacity: 0.7;
            margin-top: 0.25rem;
        }
        
        .message-content {
            white-space: pre-wrap;
            line-height: 1.4;
        }
        
        .input-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 1rem;
            padding: 1rem;
            display: flex;
            gap: 0.75rem;
        }
        
        .chat-input {
            flex: 1;
            border: 2px solid #e0e0e0;
            border-radius: 0.75rem;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }
        
        .chat-input:focus {
            border-color: #007AFF;
        }
        
        .send-button {
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 0.75rem;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .send-button:hover {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            color: #fff;
            font-style: italic;
        }

        .typing-dots {
            display: flex;
            gap: 0.25rem;
        }

        .typing-dots span {
            width: 6px;
            height: 6px;
            background: #fff;
            border-radius: 50%;
            animation: typing 1.5s infinite;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }

        .progress-panel {
            display: none;
            background: #1a1a2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            max-height: 200px;
            overflow-y: auto;
        }

        .progress-panel.active {
            display: block;
        }

        .progress-status {
            color: #4CAF50;
            font-weight: bold;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .progress-status .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid #333;
            border-top-color: #4CAF50;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .log-entries {
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #888;
        }

        .log-entry {
            padding: 0.25rem 0;
            border-bottom: 1px solid #222;
        }

        .log-entry:last-child {
            border-bottom: none;
        }

        .log-entry .timestamp {
            color: #666;
            margin-right: 0.5rem;
        }

        .log-entry .message {
            color: #aaa;
        }

        .welcome-message {
            text-align: center;
            color: #666;
            margin: 2rem 0;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .header {
                padding: 1rem;
            }
            
            .chat-container {
                padding: 0.5rem;
            }
            
            .message {
                max-width: 95%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 ADK Stock Chat Assistant</h1>
        <p>Ask me anything about stocks, get recommendations, and analyze market sentiment</p>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                👋 Welcome! I'm your AI stock analysis assistant.<br>
                Try asking me: "Give me stock recommendations" or "Analyze AAPL stock"
            </div>
        </div>
        
        <div class="progress-panel" id="progressPanel">
            <div class="progress-status">
                <div class="spinner"></div>
                <span id="progressStatus">Initializing...</span>
            </div>
            <div class="log-entries" id="logEntries"></div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            <span id="typingText">Assistant is working</span>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="input-container">
            <input 
                type="text" 
                id="chatInput" 
                class="chat-input" 
                placeholder="Ask me about stocks, recommendations, market analysis..."
                maxlength="500"
            >
            <button id="sendButton" class="send-button">Send</button>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatInput = document.getElementById('chatInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');
        const typingText = document.getElementById('typingText');
        const progressPanel = document.getElementById('progressPanel');
        const progressStatus = document.getElementById('progressStatus');
        const logEntries = document.getElementById('logEntries');

        // Load chat history on page load
        loadChatHistory();

        // Event listeners
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        sendButton.addEventListener('click', sendMessage);

        async function sendMessage() {
            const message = chatInput.value.trim();
            if (!message) return;

            // Clear input and disable send button
            chatInput.value = '';
            sendButton.disabled = true;

            // Add user message to chat
            addMessage('user', message);

            // Show typing indicator and progress panel
            showTypingIndicator();
            showProgressPanel();
            clearLogs();

            // Check if this is an analysis request (use streaming)
            const isAnalysisRequest = /recommend|analyze|sentiment|market|overview/i.test(message);

            if (isAnalysisRequest) {
                await sendStreamingMessage(message);
            } else {
                await sendRegularMessage(message);
            }
        }

        async function sendStreamingMessage(message) {
            try {
                const response = await fetch('/api/chat/stream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = line.slice(6);
                            if (data === '[DONE]') {
                                hideProgressPanel();
                                hideTypingIndicator();
                                sendButton.disabled = false;
                                chatInput.focus();
                                return;
                            }
                            try {
                                const parsed = JSON.parse(data);
                                handleStreamEvent(parsed);
                            } catch (e) {
                                console.log('Parse error:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                addMessage('assistant', 'Sorry, I couldn\\'t process your request. Please try again.');
                console.error('Streaming error:', error);
            } finally {
                hideProgressPanel();
                hideTypingIndicator();
                sendButton.disabled = false;
                chatInput.focus();
            }
        }

        function handleStreamEvent(event) {
            if (event.type === 'log') {
                // Real-time log from Python logger
                addLog(event.log);
            } else if (event.type === 'progress') {
                updateProgress(event.step, event.message);
                addLog(event.log || event.message);
            } else if (event.type === 'response') {
                addMessage('assistant', event.response);
            } else if (event.type === 'error') {
                addMessage('assistant', 'Error: ' + event.error);
            }
        }

        async function sendRegularMessage(message) {
            try {
                const response = await fetch('/api/chat/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();

                if (response.ok) {
                    addMessage('assistant', data.response);
                } else {
                    addMessage('assistant', 'Sorry, I encountered an error: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                addMessage('assistant', 'Sorry, I couldn\\'t process your request. Please try again.');
                console.error('Error sending message:', error);
            } finally {
                hideProgressPanel();
                hideTypingIndicator();
                sendButton.disabled = false;
                chatInput.focus();
            }
        }

        function addMessage(role, content) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;

            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = new Date().toLocaleTimeString();

            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(timeDiv);

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function showTypingIndicator() {
            typingIndicator.style.display = 'flex';
            typingText.textContent = 'Assistant is working';
        }

        function hideTypingIndicator() {
            typingIndicator.style.display = 'none';
        }

        function showProgressPanel() {
            progressPanel.classList.add('active');
            progressStatus.textContent = 'Initializing...';
        }

        function hideProgressPanel() {
            progressPanel.classList.remove('active');
        }

        function updateProgress(step, message) {
            progressStatus.textContent = message;
            typingText.textContent = message;
        }

        function addLog(message) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';

            const timestamp = document.createElement('span');
            timestamp.className = 'timestamp';
            timestamp.textContent = new Date().toLocaleTimeString();

            const msg = document.createElement('span');
            msg.className = 'message';
            msg.textContent = message;

            entry.appendChild(timestamp);
            entry.appendChild(msg);
            logEntries.appendChild(entry);
            // Keep only the latest 10 log entries, similar to `tail`
            while (logEntries.children.length > 10) {
                logEntries.removeChild(logEntries.firstChild);
            }
            logEntries.scrollTop = logEntries.scrollHeight;
        }

        function clearLogs() {
            logEntries.innerHTML = '';
        }
        
        async function loadChatHistory() {
            try {
                const response = await fetch('/api/chat/history');
                const data = await response.json();
                
                if (response.ok && data.history) {
                    // Clear welcome message
                    chatMessages.innerHTML = '';
                    
                    // Add messages from history
                    data.history.forEach(msg => {
                        addMessage(msg.role, msg.content);
                    });
                    
                    // If no history, show welcome message
                    if (data.history.length === 0) {
                        chatMessages.innerHTML = `
                            <div class="welcome-message">
                                👋 Welcome! I'm your AI stock analysis assistant.<br>
                                Try asking me: "Give me stock recommendations" or "Analyze AAPL stock"
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
            }
        }
        
        // Auto-focus on input
        chatInput.focus();
    </script>
</body>
</html>
        """.strip()
