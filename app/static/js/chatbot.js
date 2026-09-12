document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const newChatBtn = document.getElementById('new-chat-btn');

    // Manage session ID in localStorage
    let sessionId = localStorage.getItem('codec_chatbot_session_id');
    if (!sessionId) {
        sessionId = generateUUID();
        localStorage.setItem('codec_chatbot_session_id', sessionId);
    }

    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    function formatTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendMessage(sender, text) {
        const row = document.createElement('div');
        row.className = `message-row ${sender}-row`;

        if (sender === 'bot') {
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'bot-msg-avatar';
            avatarDiv.innerHTML = `
                <svg viewBox="0 0 48 48" class="bot-avatar-inner" fill="none">
                    <rect x="8" y="14" width="32" height="26" rx="10" fill="#2563eb" />
                    <path d="M24 6V14" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>
                    <circle cx="24" cy="5" r="3" fill="#60a5fa"/>
                    <rect x="14" y="20" width="20" height="14" rx="6" fill="#0f172a" />
                    <circle cx="19" cy="27" r="2.5" fill="#38bdf8" />
                    <circle cx="29" cy="27" r="2.5" fill="#38bdf8" />
                    <rect x="5" y="22" width="3" height="8" rx="1.5" fill="#60a5fa"/>
                    <rect x="40" y="22" width="3" height="8" rx="1.5" fill="#60a5fa"/>
                </svg>
            `;
            row.appendChild(avatarDiv);
        }

        const groupDiv = document.createElement('div');
        groupDiv.className = 'msg-bubble-group';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `msg-bubble ${sender}-bubble`;
        
        const p = document.createElement('p');
        p.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
        bubbleDiv.appendChild(p);

        const timeSpan = document.createElement('span');
        timeSpan.className = 'msg-time';
        timeSpan.textContent = formatTime();

        groupDiv.appendChild(bubbleDiv);
        groupDiv.appendChild(timeSpan);

        row.appendChild(groupDiv);
        chatMessages.appendChild(row);
        scrollToBottom();
    }

    function escapeHtml(string) {
        const entityMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        };
        return String(string).replace(/[&<>"']/g, function (s) {
            return entityMap[s];
        });
    }

    function showTyping() {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    function hideTyping() {
        typingIndicator.style.display = 'none';
    }

    async function sendMessage(messageText) {
        if (!messageText || messageText.trim() === '') return;

        const trimmed = messageText.trim();
        appendMessage('user', trimmed);
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;
        showTyping();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: trimmed,
                    session_id: sessionId
                })
            });

            const data = await response.json();
            hideTyping();

            if (response.ok) {
                appendMessage('bot', data.response);
            } else {
                appendMessage('bot', data.response || 'Sorry, something went wrong. Please try again.');
            }
        } catch (error) {
            hideTyping();
            console.error('Chat error:', error);
            appendMessage('bot', 'Network error. Please check your connection and try again.');
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    }

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage(userInput.value);
    });

    // Handle Quick Action Cards and Popular Question Pills
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.action-chip');
        if (chip) {
            const query = chip.getAttribute('data-query');
            if (query) {
                sendMessage(query);
            }
        }
    });

    // Start New Chat / Reset Session
    newChatBtn.addEventListener('click', async () => {
        sessionId = generateUUID();
        localStorage.setItem('codec_chatbot_session_id', sessionId);
        
        chatMessages.innerHTML = '';
        
        // Render initial welcome message matching Reference 1
        const welcomeRow = document.createElement('div');
        welcomeRow.className = 'message-row bot-row';
        welcomeRow.innerHTML = `
            <div class="bot-msg-avatar">
                <svg viewBox="0 0 48 48" class="bot-avatar-inner" fill="none">
                    <rect x="8" y="14" width="32" height="26" rx="10" fill="#2563eb" />
                    <path d="M24 6V14" stroke="#2563eb" stroke-width="3" stroke-linecap="round"/>
                    <circle cx="24" cy="5" r="3" fill="#60a5fa"/>
                    <rect x="14" y="20" width="20" height="14" rx="6" fill="#0f172a" />
                    <circle cx="19" cy="27" r="2.5" fill="#38bdf8" />
                    <circle cx="29" cy="27" r="2.5" fill="#38bdf8" />
                    <rect x="5" y="22" width="3" height="8" rx="1.5" fill="#60a5fa"/>
                    <rect x="40" y="22" width="3" height="8" rx="1.5" fill="#60a5fa"/>
                </svg>
            </div>
            <div class="msg-bubble-group">
                <div class="msg-bubble bot-bubble">
                    <p>Hello! 👋 I'm your AI Customer Support Assistant.<br>How can I help you today?</p>
                </div>
                <span class="msg-time">Just now</span>
            </div>
        `;
        chatMessages.appendChild(welcomeRow);
        userInput.focus();
    });
});
