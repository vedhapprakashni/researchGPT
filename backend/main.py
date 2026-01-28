"""
ResearchGPT Backend - FastAPI Application
AI-powered Research Paper Assistant using RAG
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .services.vector_store import VectorStore

# Load environment variables
load_dotenv()

# Global vector store instance
vector_store: VectorStore = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - initialize and cleanup resources"""
    global vector_store
    
    # Initialize Pinecone on startup
    print("🚀 Initializing ResearchGPT backend...")
    vector_store = VectorStore()
    await vector_store.initialize()
    print("✅ Vector store connected")
    
    yield
    
    # Cleanup on shutdown
    print("👋 Shutting down ResearchGPT backend...")


app = FastAPI(
    title="ResearchGPT API",
    description="AI-powered Research Paper Assistant using RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers AFTER app is created to avoid circular imports
from .routers import papers, qa, groups

# Include routers
app.include_router(papers.router, prefix="/api", tags=["Papers"])
app.include_router(qa.router, prefix="/api", tags=["Q&A"])
app.include_router(groups.router, prefix="/api", tags=["Groups"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ResearchGPT API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "vector_store": "connected" if vector_store else "disconnected"
    }


def get_vector_store() -> VectorStore:
    """Dependency to get vector store instance"""
    return vector_store
