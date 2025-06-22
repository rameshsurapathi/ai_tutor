async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (message) {
        // Add user message to chat immediately
        addMessage(message, 'user');
        input.value = '';
        
        // Show typing indicator while waiting for AI
        showTypingIndicator();
        
        try {
            // Send message to your Python backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    subject: getCurrentSubject()
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Add AI teacher's response to chat
            addMessage(data.response, 'bot');
            
        } catch (error) {
            console.error('Error:', error);
            removeTypingIndicator();
            addMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
        }
    }
}

function getCurrentSubject() {
    const activeTab = document.querySelector('.tab.active');
    const tabText = activeTab.textContent.toLowerCase();
    
    if (tabText.includes('physics')) return 'physics';
    if (tabText.includes('chemistry')) return 'chemistry';
    if (tabText.includes('math')) return 'maths';
    return 'maths'; // default
}

function showTypingIndicator() {
    const chatSection = document.querySelector('.chat-section');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="chat-message bot-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <span class="message-time" style="font-size:16px;color:black;">Thinking...</span>
            </div>
        </div>
    `;
    chatSection.appendChild(typingDiv);
    chatSection.scrollTop = chatSection.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function addMessage(text, sender) {
    const chatSection = document.querySelector('.chat-section');
    const messageDiv = document.createElement('div');
    const currentTime = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="chat-message user-message" style="flex-direction: row-reverse;">
                <div class="message-avatar" style="background: #10b981;">👤</div>
                <div class="message-content" style="background: #667eea; color: white;">
                    <p style="color: rgba(255,255,255,0.8);">${text}</p>
                    <span class="message-time" style="color: rgba(255,255,255,0.8);">${currentTime}</span>
                </div>
            </div>
        `;
    } else {
        // If the response looks like HTML, render as HTML. Otherwise, convert newlines to <br> for plain text.
        let isHTML = /<[a-z][\s\S]*>/i.test(text.trim());
        let safeText = text;
        if (!isHTML) {
            safeText = text.replace(/\n/g, '<br>');
        }
        messageDiv.innerHTML = `
        <div class="chat-message bot-message">
        <div class="message-avatar">👨‍🏫</div>
        <div class="message-content">
            <div class="response-text">${safeText}</div>
            <span class="message-time">${currentTime}</span>
        </div>
        </div>`;
    }
    
    chatSection.appendChild(messageDiv);
    chatSection.scrollTop = chatSection.scrollHeight;
}

// Handle Enter key press
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Handle example clicks
document.addEventListener('DOMContentLoaded', function() {
    const exampleItems = document.querySelectorAll('.example-item');
    exampleItems.forEach(item => {
        item.addEventListener('click', function() {
            const questionText = this.querySelector('span:last-child').textContent;
            document.getElementById('messageInput').value = questionText;
            sendMessage();
        });
    });
    
    // Handle tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
