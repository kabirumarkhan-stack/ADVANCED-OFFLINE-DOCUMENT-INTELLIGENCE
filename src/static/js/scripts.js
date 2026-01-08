document.addEventListener('DOMContentLoaded', () => {
    // Chat functionality
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');

    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = `<div class="message-bubble">${content}</div>`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Add welcome message
    addMessage('Welcome! Upload documents using the 📎 button, then ask me questions about them.', 'ai');

    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async () => {
        const files = fileInput.files;
        if (files.length > 0) {
            addMessage(`Uploading ${files.length} document(s)...`, 'user');
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            try {
                const response = await fetch('/upload', { method: 'POST', body: formData });
                const data = await response.json();
                if (response.ok) {
                    addMessage('Documents uploaded successfully.', 'ai');
                } else {
                    addMessage('Upload failed.', 'ai');
                }
            } catch (error) {
                addMessage('Upload error.', 'ai');
            }
        }
    });

    sendBtn.addEventListener('click', async () => {
        const query = messageInput.value.trim();
        if (query) {
            addMessage(query, 'user');
            messageInput.value = '';
            addMessage('Thinking...', 'ai');
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                const data = await response.json();
                const lastMessage = chatMessages.lastElementChild;
                lastMessage.innerHTML = `<div class="message-bubble">${window.marked.parse(data.answer)}</div>`;
                if (data.sources.length > 0) {
                    addMessage('Sources: ' + data.sources.join(', '), 'ai');
                }
            } catch (error) {
                const lastMessage = chatMessages.lastElementChild;
                lastMessage.innerHTML = `<div class="message-bubble">Error.</div>`;
            }
        }
    });

    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });
});