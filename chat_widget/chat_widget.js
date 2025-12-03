// Chat Widget JavaScript
class ChatWidget {
    constructor() {
        this.isOpen = false;
        this.currentLanguage = 'en';
        this.sessionId = this.generateSessionId();
        this.userId = this.getUserId();
        this.pendingFeedback = null;
        
        // API endpoint - change this to your actual chatbot service URL
        this.apiEndpoint = 'http://localhost:8000';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateLanguageDisplay();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    getUserId() {
        // Try to get user ID from localStorage, cookies, or generate anonymous ID
        let userId = localStorage.getItem('chat_user_id');
        if (!userId) {
            userId = 'anon_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('chat_user_id', userId);
        }
        return userId;
    }
    
    setupEventListeners() {
        // Toggle chat window
        document.getElementById('chat-toggle').addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Minimize chat
        document.getElementById('chat-minimize').addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Language toggle
        document.getElementById('language-toggle').addEventListener('click', () => {
            this.toggleLanguage();
        });
        
        // Send message
        document.getElementById('chat-send').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter key to send message
        document.getElementById('chat-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Feedback modal events
        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectFeedback(e.target.dataset.feedback);
            });
        });
        
        document.getElementById('feedback-submit').addEventListener('click', () => {
            this.submitFeedback();
        });
        
        document.getElementById('feedback-skip').addEventListener('click', () => {
            this.hideFeedbackModal();
        });
        
        // Close feedback modal when clicking outside
        document.getElementById('feedback-modal').addEventListener('click', (e) => {
            if (e.target.id === 'feedback-modal') {
                this.hideFeedbackModal();
            }
        });
    }
    
    toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatWindow.classList.add('show');
            this.hideNotificationBadge();
            // Focus input when opened
            setTimeout(() => {
                document.getElementById('chat-input').focus();
            }, 300);
        } else {
            chatWindow.classList.remove('show');
        }
    }
    
    toggleLanguage() {
        this.currentLanguage = this.currentLanguage === 'en' ? 'ar' : 'en';
        this.updateLanguageDisplay();
        this.updateWelcomeMessage();
    }
    
    updateLanguageDisplay() {
        const languageToggle = document.getElementById('language-toggle');
        languageToggle.textContent = this.currentLanguage.toUpperCase();
        
        // Update input placeholder
        const chatInput = document.getElementById('chat-input');
        if (this.currentLanguage === 'ar') {
            chatInput.placeholder = 'اكتب رسالتك...';
            chatInput.style.direction = 'rtl';
        } else {
            chatInput.placeholder = 'Type your message...';
            chatInput.style.direction = 'ltr';
        }
    }
    
    updateWelcomeMessage() {
        const welcomeMessage = document.getElementById('welcome-message');
        const messages = {
            en: "Hello! I'm your AI assistant. How can I help you today?",
            ar: "مرحباً! أنا مساعدك الذكي. كيف يمكنني مساعدتك اليوم؟"
        };
        welcomeMessage.textContent = messages[this.currentLanguage];
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Clear input and disable send button
        input.value = '';
        this.setSendButtonState(false);
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to API
            const response = await this.callChatAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(response.response, 'bot', {
                confidence: response.confidence,
                category: response.category,
                messageId: Date.now() // Use timestamp as simple message ID
            });
            
            // Show feedback modal if confidence is low or after delay
            if (response.confidence < 0.7) {
                setTimeout(() => {
                    this.showFeedbackModal();
                }, 1000);
            }
            
        } catch (error) {
            console.error('Chat API error:', error);
            this.hideTypingIndicator();
            
            const errorMessage = this.currentLanguage === 'ar' 
                ? 'عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.'
                : 'Sorry, there was an error. Please try again.';
                
            this.addMessage(errorMessage, 'bot', { isError: true });
        } finally {
            this.setSendButtonState(true);
        }
    }
    
    async callChatAPI(message) {
        const response = await fetch(`${this.apiEndpoint}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: this.currentLanguage,
                session_id: this.sessionId,
                user_id: this.userId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(text, sender, metadata = {}) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        let actionsHtml = '';
        if (sender === 'bot' && !metadata.isError) {
            actionsHtml = `
                <div class="message-actions">
                    <button class="feedback-btn-small" data-feedback="like" data-message-id="${metadata.messageId}">👍</button>
                    <button class="feedback-btn-small" data-feedback="dislike" data-message-id="${metadata.messageId}">👎</button>
                </div>
            `;
        }
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${time}</div>
                ${actionsHtml}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        // Add event listeners for inline feedback buttons
        if (actionsHtml) {
            const feedbackBtns = messageDiv.querySelectorAll('.feedback-btn-small');
            feedbackBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.handleInlineFeedback(e.target);
                });
            });
        }
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Show notification if chat is closed
        if (!this.isOpen) {
            this.showNotificationBadge();
        }
    }
    
    formatMessage(text) {
        // Basic formatting - can be enhanced
        return text.replace(/\n/g, '<br>');
    }
    
    handleInlineFeedback(button) {
        const feedback = button.dataset.feedback;
        const messageId = button.dataset.messageId;
        
        // Visual feedback
        const parentActions = button.parentElement;
        parentActions.querySelectorAll('.feedback-btn-small').forEach(btn => {
            btn.classList.remove('selected');
        });
        button.classList.add('selected');
        
        // Send feedback to API
        this.sendFeedback(feedback, null, messageId);
    }
    
    async sendFeedback(feedbackType, comment = null, messageId = null) {
        try {
            await fetch(`${this.apiEndpoint}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    feedback_type: feedbackType,
                    comment: comment
                })
            });
        } catch (error) {
            console.error('Feedback API error:', error);
        }
    }
    
    showTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        indicator.style.display = 'block';
        
        const text = this.currentLanguage === 'ar' ? 'الذكي الاصطناعي يكتب' : 'AI is typing';
        indicator.innerHTML = `${text}<span class="dots">...</span>`;
    }
    
    hideTypingIndicator() {
        document.getElementById('typing-indicator').style.display = 'none';
    }
    
    setSendButtonState(enabled) {
        const sendBtn = document.getElementById('chat-send');
        sendBtn.disabled = !enabled;
        sendBtn.textContent = enabled ? 'Send' : 'Sending...';
    }
    
    showFeedbackModal() {
        this.pendingFeedback = { sessionId: this.sessionId };
        document.getElementById('feedback-modal').style.display = 'flex';
    }
    
    hideFeedbackModal() {
        document.getElementById('feedback-modal').style.display = 'none';
        this.pendingFeedback = null;
        
        // Reset modal state
        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.getElementById('feedback-comment').value = '';
    }
    
    selectFeedback(feedbackType) {
        if (!this.pendingFeedback) return;
        
        this.pendingFeedback.type = feedbackType;
        
        // Update UI
        document.querySelectorAll('.feedback-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.querySelector(`[data-feedback="${feedbackType}"]`).classList.add('selected');
    }
    
    async submitFeedback() {
        if (!this.pendingFeedback || !this.pendingFeedback.type) return;
        
        const comment = document.getElementById('feedback-comment').value.trim();
        
        try {
            await this.sendFeedback(this.pendingFeedback.type, comment);
            this.hideFeedbackModal();
            
            // Show thank you message
            const thankYouMessage = this.currentLanguage === 'ar' 
                ? 'شكراً لك على ملاحظاتك!'
                : 'Thank you for your feedback!';
                
            this.addMessage(thankYouMessage, 'bot', { isSystem: true });
            
        } catch (error) {
            console.error('Feedback submission error:', error);
        }
    }
    
    showNotificationBadge() {
        const badge = document.getElementById('chat-badge');
        badge.style.display = 'flex';
        
        // Simple notification count (can be enhanced)
        const currentCount = parseInt(badge.textContent) || 0;
        badge.textContent = currentCount + 1;
    }
    
    hideNotificationBadge() {
        const badge = document.getElementById('chat-badge');
        badge.style.display = 'none';
        badge.textContent = '1';
    }
}

// Initialize chat widget when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatWidget();
});

// Global function to open chat (can be called from anywhere)
window.openChat = function() {
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow.classList.contains('show')) {
        document.getElementById('chat-toggle').click();
    }
};

// Global function to send predefined message
window.sendChatMessage = function(message) {
    window.openChat();
    setTimeout(() => {
        const input = document.getElementById('chat-input');
        input.value = message;
        document.getElementById('chat-send').click();
    }, 500);
};
