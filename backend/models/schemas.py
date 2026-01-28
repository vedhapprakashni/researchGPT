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


# ============ Group Models ============

class PaperGroup(BaseModel):
    """Paper group for multi-document queries"""
    group_id: str
    name: str
    description: Optional[str] = None
    paper_ids: List[str] = []
    created_date: datetime


class GroupCreate(BaseModel):
    """Request to create a new group"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    paper_ids: List[str] = []


class GroupUpdate(BaseModel):
    """Request to update a group"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    add_papers: Optional[List[str]] = None
    remove_papers: Optional[List[str]] = None


class GroupListResponse(BaseModel):
    """Response for listing groups"""
    groups: List[PaperGroup]
    total: int


class GroupDeleteResponse(BaseModel):
    """Response after deleting a group"""
    success: bool
    group_id: str
    message: str


# ============ Q&A Models ============

class QuestionRequest(BaseModel):
    """Request to ask a question"""
    question: str = Field(..., min_length=3, max_length=1000)
    paper_id: Optional[str] = None  # If None, search all papers
    group_id: Optional[str] = None  # If set, query all papers in this group
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
