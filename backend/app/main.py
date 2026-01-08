from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Document Q&A RAG API",
    description="Backend API for Document Question & Answer system using RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Document Q&A RAG API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running"
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint"""
    # Test MongoDB connection
    mongodb_status = "connected"
    try:
        from app.utils.database import get_database
        db = get_database()
        if db is None:
            mongodb_status = "disconnected"
    except Exception as e:
        mongodb_status = f"error: {str(e)}"
    
    # Test Ollama connection
    ollama_status = "connected"
    try:
        import requests
        from app.config import settings
        response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/version", timeout=2)
        if response.status_code != 200:
            ollama_status = "disconnected"
    except Exception as e:
        ollama_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "mongodb": mongodb_status,
        "ollama": ollama_status,
        "chromadb": "initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)