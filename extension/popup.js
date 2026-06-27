document.addEventListener('DOMContentLoaded', async () => {
  const chatbox = document.getElementById('chatbox');
  const queryInput = document.getElementById('query');
  const sendBtn = document.getElementById('sendBtn');
  const welcomeScreen = document.getElementById('welcomeScreen');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const loadingText = document.getElementById('loadingText');
  const statusIndicator = document.getElementById('statusIndicator');
  const chatArea = document.querySelector('.chat-area');

  function updateStatus(state, text) {
    statusIndicator.className = `status-indicator ${state}`;
    statusIndicator.querySelector('.status-text').textContent = text;
  }

  function appendMessage(sender, text) {
    welcomeScreen.style.display = 'none';
    chatbox.style.display = 'flex';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender.toLowerCase()}`;
    
    const senderName = document.createElement('div');
    senderName.className = 'message-sender';
    senderName.textContent = sender;
    
    const textNode = document.createElement('div');
    textNode.textContent = text;
    
    messageDiv.appendChild(senderName);
    messageDiv.appendChild(textNode);
    chatbox.appendChild(messageDiv);
    
    chatArea.scrollTop = chatArea.scrollHeight;
  }

  async function handleSend(question) {
    if (!question.trim()) return;
    
    appendMessage('You', question);
    queryInput.value = '';
    
    // Disable inputs & show loading
    queryInput.disabled = true;
    sendBtn.disabled = true;
    loadingSpinner.style.display = 'flex';
    loadingText.textContent = "Processing transcript...";
    updateStatus('loading', 'Thinking...');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_id: currentVideoId, question: question })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Server error');
      }
      
      const data = await response.json();
      appendMessage('AI', data.response);
      updateStatus('ready', 'Connected');
    } catch (err) {
      appendMessage('AI', `Error: ${err.message || 'Could not connect to backend.'}`);
      updateStatus('error', 'Error');
    } finally {
      queryInput.disabled = false;
      sendBtn.disabled = false;
      loadingSpinner.style.display = 'none';
      queryInput.focus();
    }
  }

  // Get current active tab
  let currentVideoId = null;
  
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url && tab.url.includes("youtube.com/watch")) {
      const urlParams = new URLSearchParams(new URL(tab.url).search);
      currentVideoId = urlParams.get('v');
      
      if (currentVideoId) {
        queryInput.disabled = false;
        sendBtn.disabled = false;
        updateStatus('ready', 'Connected');
        
        // Wire send button
        sendBtn.addEventListener('click', () => handleSend(queryInput.value));
        queryInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            handleSend(queryInput.value);
          }
        });
        
        // Wire quick-prompts
        document.querySelectorAll('.quick-btn').forEach(btn => {
          btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            handleSend(prompt);
          });
        });
      } else {
        showErrorState("Could not parse YouTube video ID.");
      }
    } else {
      showErrorState("Please navigate to a YouTube video page to start chatting.");
    }
  } catch (e) {
    showErrorState("Chrome extensions APIs unavailable or blocked.");
  }

  function showErrorState(message) {
    welcomeScreen.innerHTML = `
      <div class="welcome-icon">⚠️</div>
      <h2>Not on YouTube</h2>
      <p>${message}</p>
    `;
    updateStatus('error', 'Inactive');
    queryInput.disabled = true;
    sendBtn.disabled = true;
  }
});
