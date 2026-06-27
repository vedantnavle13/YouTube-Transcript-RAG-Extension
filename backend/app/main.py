from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.services.transcript import TranscriptService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YouTube Transcript RAG API",
    description="A FastAPI backend to scrape YouTube transcripts and query them using FAISS & Gemini LLM"
)

# CORS middleware config to allow requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local extensions
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    video_id: str
    question: str

# Lazy initialization of RAGEngine to allow uvicorn to boot up even without a configured API key
rag_engine_instance = None

def get_rag_engine():
    global rag_engine_instance
    if rag_engine_instance is None:
        from backend.app.services.rag_engine import RAGEngine
        rag_engine_instance = RAGEngine()
    return rag_engine_instance

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: ChatRequest):
    video_id = request.video_id
    question = request.question
    
    if not video_id:
        raise HTTPException(status_code=400, detail="video_id is required")
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
        
    try:
        # Get RAG Engine (this will validate the GEMINI_API_KEY)
        engine = get_rag_engine()
        
        # Check if the vector store index already exists for this video
        if not engine.index_exists(video_id):
            logger.info(f"Index not found for video {video_id}. Fetching transcript...")
            transcript_text = TranscriptService.get_transcript(video_id)
            logger.info(f"Transcript fetched successfully. Creating vector index...")
            engine.create_index(video_id, transcript_text)
            logger.info(f"Vector index created successfully for video {video_id}.")
        
        # Query the RAG engine
        logger.info(f"Querying RAG engine for video {video_id}...")
        answer = engine.query(video_id, question)
        return {"response": answer}
        
    except ValueError as val_err:
        logger.error(f"Configuration error: {str(val_err)}")
        raise HTTPException(status_code=500, detail=str(val_err))
    except Exception as e:
        logger.error(f"Error handling chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
