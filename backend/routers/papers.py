"""
Papers Router
Endpoints for uploading, listing, and deleting papers
"""
import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..models.schemas import (
    PaperUploadResponse,
    PaperListResponse,
    PaperDeleteResponse,
    PaperMetadata
)
from ..services.pdf_parser import PDFParser
from ..services.chunker import TextChunker

router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Paper metadata storage (simple JSON file)
METADATA_FILE = UPLOAD_DIR / "papers_metadata.json"


def load_papers_metadata() -> dict:
    """Load paper metadata from JSON file"""
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text())
    return {}


def save_papers_metadata(metadata: dict):
    """Save paper metadata to JSON file"""
    METADATA_FILE.write_text(json.dumps(metadata, indent=2, default=str))


def get_vector_store():
    """Get vector store from main module"""
    from ..main import vector_store
    return vector_store


@router.post("/upload_paper", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...)
):
    """
    Upload a research paper PDF
    
    The paper will be:
    1. Saved to disk
    2. Parsed to extract text and sections
    3. Chunked into smaller pieces
    4. Embedded and stored in vector database
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Generate unique paper ID
    paper_id = str(uuid.uuid4())[:8]
    
    # Save file to disk
    file_path = UPLOAD_DIR / f"{paper_id}_{file.filename}"
    
    try:
        content = await file.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        # Parse PDF
        parser = PDFParser()
        sections, title, total_pages = parser.extract_text_by_section(str(file_path))
        
        if not sections:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Chunk the document
        chunker = TextChunker()
        chunks = chunker.chunk_document(sections, paper_id)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Document too short to process")
        
        # Get vector store and upsert chunks
        vs = get_vector_store()
        await vs.upsert_chunks(chunks)
        
        # Save paper metadata
        metadata = load_papers_metadata()
        metadata[paper_id] = {
            "paper_id": paper_id,
            "filename": file.filename,
            "title": title,
            "upload_date": datetime.now().isoformat(),
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "file_path": str(file_path)
        }
        save_papers_metadata(metadata)
        
        return PaperUploadResponse(
            success=True,
            paper_id=paper_id,
            filename=file.filename,
            message=f"Successfully processed paper: {title}",
            total_chunks=len(chunks),
            total_pages=total_pages
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@router.get("/list_papers", response_model=PaperListResponse)
async def list_papers():
    """
    List all uploaded papers
    """
    metadata = load_papers_metadata()
    
    papers = [
        PaperMetadata(
            paper_id=data["paper_id"],
            filename=data["filename"],
            title=data.get("title"),
            upload_date=datetime.fromisoformat(data["upload_date"]),
            total_pages=data.get("total_pages", 0),
            total_chunks=data.get("total_chunks", 0)
        )
        for data in metadata.values()
    ]
    
    # Sort by upload date (newest first)
    papers.sort(key=lambda p: p.upload_date, reverse=True)
    
    return PaperListResponse(
        papers=papers,
        total=len(papers)
    )


@router.delete("/delete_paper/{paper_id}", response_model=PaperDeleteResponse)
async def delete_paper(paper_id: str):
    """
    Delete a paper and its vectors from the database
    """
    metadata = load_papers_metadata()
    
    if paper_id not in metadata:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    paper_data = metadata[paper_id]
    
    try:
        # Delete from vector store
        vs = get_vector_store()
        await vs.delete_paper(paper_id)
        
        # Delete file from disk
        file_path = Path(paper_data.get("file_path", ""))
        if file_path.exists():
            file_path.unlink()
        
        # Remove from metadata
        del metadata[paper_id]
        save_papers_metadata(metadata)
        
        return PaperDeleteResponse(
            success=True,
            paper_id=paper_id,
            message=f"Successfully deleted paper: {paper_data.get('title', paper_id)}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete paper: {str(e)}")


@router.get("/paper/{paper_id}")
async def get_paper(paper_id: str):
    """
    Get details of a specific paper
    """
    metadata = load_papers_metadata()
    
    if paper_id not in metadata:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    return metadata[paper_id]
