# YouTube Transcript RAG Extension

A powerful Chrome Extension and FastAPI backend that allows you to chat with any YouTube video in real-time. It retrieves the video's transcript, splits it into semantic chunks, creates local vector indexes using FAISS & Google Generative AI Embeddings, and answers queries using the `gemini-2.5-flash` model.

---

## 🚀 Features

- **On-Demand RAG**: Automatically downloads and indexes transcripts only when a video is queried for the first time.
- **Fast Local Vector Caching**: Saves FAISS index files locally under `backend/data/` so subsequent queries get instant, sub-second responses.
- **Premium UI Design**: A sleek glassmorphic popup containing connection health animations, chat history, typing indicators, and quick summary shortcuts.
- **LangChain Expression Language (LCEL)**: Uses a structured pipeline to format context and retrieve relevant snippets.

---

## 📂 Project Structure

```text
youtube-rag-extension/
├── backend/                  # Python FastAPI Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # API endpoints & server initialization
│   │   ├── config.py         # Environment variables & API keys
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── transcript.py # Handles YouTube transcript scraping/cleaning
│   │       └── rag_engine.py # Handles FAISS, LangChain, & Gemini LLM
│   ├── data/                 # Local directory for FAISS vector indexes
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment secrets (GEMINI_API_KEY)
│
└── extension/                # Chrome Extension Frontend
    ├── manifest.json         # Extension configuration (v3)
    ├── popup.html            # UI view layout
    ├── popup.js              # UI interaction & API communication
    └── styles.css            # Styling for the extension popup
```

---

## 🛠️ Local Setup & Installation

### 1. Configure the Backend

1. **Activate your virtual environment**:
   ```bash
   source .venv/bin/activate
   ```
2. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configure Environment Secrets**:
   Create or edit the file `backend/.env` and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. **Start the server**:
   ```bash
   python3 -m uvicorn backend.app.main:app --reload
   ```
   *Your server will boot and run on `http://127.0.0.1:8000`.*

---

### 2. Install the Chrome Extension

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle the **Developer mode** switch in the top-right corner to **ON**.
3. Click the **Load unpacked** button in the top-left corner.
4. Select the `extension/` folder in this repository.

---

## 💡 How to Use

1. Go to any YouTube video watch page (e.g. `https://www.youtube.com/watch?v=pX2zvfD6GCY`).
2. Click the **YouTube Transcript AI Chat** icon from your Chrome extensions bar.
3. The status indicator in the top-right corner will pulse green and show **Connected**.
4. Click **Summarize Video** or type a custom question in the input field and hit enter to chat!

---

## 🌐 Production Deployment

If you want the extension to work anytime without running your local server:
1. Deploy the `backend/` folder on a Python hosting platform like **Render**, **Railway**, or **Hugging Face Spaces**.
2. Pass your `GEMINI_API_KEY` as a service environment variable.
3. In `extension/popup.js`, change the local fetch URL:
   ```javascript
   // Replace http://127.0.0.1:8000/chat with your deployed URL
   const response = await fetch('https://your-deployed-app.com/chat', { ... });
   ```
4. Go to `chrome://extensions/` and click the **Refresh** button on your loaded unpacked card to apply the changes.
