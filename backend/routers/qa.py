"""
Q&A Router
Endpoints for asking questions about research papers
"""
from typing import List
from fastapi import APIRouter, HTTPException

from ..models.schemas import QuestionRequest, AnswerResponse
from ..services.rag_pipeline import RAGPipeline

router = APIRouter()


def get_vector_store():
    """Get vector store from main module"""
    from ..main import vector_store
    return vector_store


@router.post("/ask_question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about uploaded research papers
    
    The question will be:
    1. Embedded using the same model as documents
    2. Used to search for relevant chunks
    3. Combined with retrieved context to generate an answer
    
    Modes:
    - academic: Formal, detailed explanation with proper terminology
    - simple: Plain language explanation, no jargon
    - eli5: "Explain Like I'm 5" - very simple analogies
    """
    import traceback
    try:
        # Get vector store and create RAG pipeline
        vs = get_vector_store()
        rag = RAGPipeline(vs)
        
        # Get answer
        result = await rag.answer_question(
            question=request.question,
            paper_id=request.paper_id,
            mode=request.mode,
            top_k=request.top_k
        )
        
        return AnswerResponse(
            answer=result["answer"],
            citations=result["citations"],
            question=result["question"],
            mode=result["mode"],
            retrieved_chunks=result["retrieved_chunks"]
        )
        
    except Exception as e:
        print(f"ERROR in ask_question: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.post("/compare_papers")
async def compare_papers(
    question: str,
    paper_ids: List[str],
    mode: str = "academic"
):
    """
    Compare multiple papers on a specific topic
    
    Retrieves relevant chunks from each specified paper
    and generates a comparative analysis.
    """
    if len(paper_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 paper IDs are required for comparison"
        )
    
    try:
        vs = get_vector_store()
        rag = RAGPipeline(vs)
        
        result = await rag.compare_papers(
            question=question,
            paper_ids=paper_ids,
            mode=mode
        )
        
        return AnswerResponse(
            answer=result["answer"],
            citations=result["citations"],
            question=result["question"],
            mode=result["mode"],
            retrieved_chunks=result["retrieved_chunks"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare papers: {str(e)}"
        )
