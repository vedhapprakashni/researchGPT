"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============ Paper Models ============

class ChunkMetadata(BaseModel):
    """Metadata for a text chunk"""
    chunk_id: str
    paper_id: str
    section: str = "Unknown"
    page: int = 0
    text: str


class PaperMetadata(BaseModel):
    """Metadata for an uploaded paper"""
    paper_id: str
    filename: str
    title: Optional[str] = None
    upload_date: datetime
    total_pages: int = 0
    total_chunks: int = 0


class PaperUploadResponse(BaseModel):
    """Response after uploading a paper"""
    success: bool
    paper_id: str
    filename: str
    message: str
    total_chunks: int = 0
    total_pages: int = 0


class PaperListResponse(BaseModel):
    """Response for listing papers"""
    papers: List[PaperMetadata]
    total: int


class PaperDeleteResponse(BaseModel):
    """Response after deleting a paper"""
    success: bool
    paper_id: str
    message: str


# ============ Q&A Models ============

class QuestionRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(..., min_length=3, max_length=1000)
    paper_id: Optional[str] = None  # If None, search all papers
    mode: str = Field(default="academic", pattern="^(academic|simple|eli5)$")
    top_k: int = Field(default=5, ge=1, le=10)


class Citation(BaseModel):
    """Citation reference in an answer"""
    paper_id: str
    page: int
    section: str
    chunk_preview: str  # First 100 chars of the chunk


class AnswerResponse(BaseModel):
    """Response with the generated answer"""
    answer: str
    citations: List[Citation]
    question: str
    mode: str
    retrieved_chunks: int


# ============ Health Models ============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_store: str
