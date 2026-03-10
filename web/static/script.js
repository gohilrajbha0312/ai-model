/*  ═══════════════════════════════════════════════════════════════
    AI Cybersecurity Assistant — Frontend JavaScript
    AJAX chat, tool execution, live interactions
    ═══════════════════════════════════════════════════════════════ */

/* ── Chat ────────────────────────────────────────────────────── */

function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    // Add user message to UI
    appendMessage('user', message);
    input.value = '';
    input.focus();

    // Show typing indicator
    const typingId = showTypingIndicator();

    // Send to server
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message }),
    })
        .then(res => res.json())
        .then(data => {
            removeTypingIndicator(typingId);
            if (data.error) {
                appendMessage('assistant', '❌ ' + data.error);
            } else {
                appendMessage('assistant', data.response, data.html);
            }
        })
        .catch(err => {
            removeTypingIndicator(typingId);
            appendMessage('assistant', '❌ Connection error: ' + err.message);
        });
}

function sendQuick(text) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        // Remove the welcome card
        const welcome = document.querySelector('.chat-welcome');
        if (welcome) welcome.remove();
        sendMessage(new Event('submit'));
    }
}

function appendMessage(role, text, htmlContent = null) {
    const container = document.getElementById('chatMessages');
    if (!container) return;

    // Remove welcome if present
    const welcome = container.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${role}`;

    // Use HTML if provided by backend, otherwise escape raw text
    const displayContent = htmlContent ? htmlContent : escapeHtml(text);

    msgDiv.innerHTML = `
        <div class="message-avatar">${role === 'user' ? '👤' : '🤖'}</div>
        <div class="message-content">
            <div class="message-text markdown-body">${displayContent}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatMessages');
    if (!container) return null;

    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.className = 'message message-assistant';
    div.id = id;
    div.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-text"><span class="spinner"></span> Thinking…</div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

/* ── Tools ───────────────────────────────────────────────────── */

function runTool(toolName, inputId) {
    const input = document.getElementById(inputId);
    const target = input ? input.value.trim() : '';

    if (!target && toolName !== 'log_analyze') {
        showToolResult('❌ Please enter a target value.');
        return;
    }

    showToolResult('<span class="spinner"></span> Running tool…');

    fetch('/api/tool', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: toolName, target: target || '/var/log' }),
    })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToolResult('❌ ' + data.error);
            } else {
                showToolResult(data.html ? `<div class="markdown-body">${data.html}</div>` : escapeHtml(data.response));
            }
        })
        .catch(err => {
            showToolResult('❌ Connection error: ' + err.message);
        });
}

function showToolResult(html) {
    const results = document.getElementById('toolResults');
    const content = document.getElementById('resultsContent');
    if (results && content) {
        content.innerHTML = html;
        results.style.display = 'block';
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function clearResults() {
    const results = document.getElementById('toolResults');
    if (results) results.style.display = 'none';
}

/* ── Utilities ───────────────────────────────────────────────── */

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/* ── Auto-scroll chat on page load ───────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Auto-dismiss flash messages after 5 seconds
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(-8px)';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
});
