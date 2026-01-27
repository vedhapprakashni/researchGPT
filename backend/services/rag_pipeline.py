"""
RAG Pipeline Service
Orchestrates retrieval and generation for Q&A
"""
from typing import List, Dict, Optional
from .vector_store import VectorStore
from .llm_service import get_llm_service
from ..models.schemas import Citation


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) Pipeline
    
    Orchestrates the full Q&A flow:
    1. Embed user question
    2. Retrieve relevant chunks from vector store
    3. Build context prompt
    4. Generate answer with LLM
    5. Extract citations
    """
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm_service = get_llm_service()
    
    async def answer_question(
        self,
        question: str,
        paper_id: Optional[str] = None,
        mode: str = "academic",
        top_k: int = 5
    ) -> Dict:
        """
        Answer a question about research paper(s)
        
        Args:
            question: User's question
            paper_id: Optional specific paper to search (None = all papers)
            mode: Response mode (academic, simple, eli5)
            top_k: Number of chunks to retrieve
            
        Returns:
            Dict with answer, citations, and metadata
        """
        # Step 1: Retrieve relevant chunks
        chunks = await self.vector_store.query(
            query_text=question,
            top_k=top_k,
            paper_id=paper_id
        )
        
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded papers to answer this question. Please make sure you've uploaded a paper that covers this topic.",
                "citations": [],
                "question": question,
                "mode": mode,
                "retrieved_chunks": 0
            }
        
        # Step 2: Generate answer with LLM
        answer = await self.llm_service.generate_answer(
            question=question,
            chunks=chunks,
            mode=mode
        )
        
        # Step 3: Build citations from retrieved chunks
        citations = self._build_citations(chunks)
        
        return {
            "answer": answer,
            "citations": citations,
            "question": question,
            "mode": mode,
            "retrieved_chunks": len(chunks)
        }
    
    def _build_citations(self, chunks: List[Dict]) -> List[Citation]:
        """Extract citations from retrieved chunks"""
        citations = []
        seen = set()  # Avoid duplicate citations
        
        for chunk in chunks:
            # Create unique key for deduplication
            key = (chunk["paper_id"], chunk["page"], chunk["section"])
            if key in seen:
                continue
            seen.add(key)
            
            citations.append(Citation(
                paper_id=chunk["paper_id"],
                page=chunk["page"],
                section=chunk["section"],
                chunk_preview=chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
            ))
        
        # Sort by page number
        citations.sort(key=lambda c: c.page)
        
        return citations
    
    async def compare_papers(
        self,
        question: str,
        paper_ids: List[str],
        mode: str = "academic"
    ) -> Dict:
        """
        Compare multiple papers on a specific topic
        
        Retrieves chunks from specified papers and asks LLM to compare
        """
        all_chunks = []
        
        for paper_id in paper_ids:
            chunks = await self.vector_store.query(
                query_text=question,
                top_k=3,
                paper_id=paper_id
            )
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return {
                "answer": "I couldn't find relevant information in the specified papers for comparison.",
                "citations": [],
                "question": question,
                "mode": mode,
                "retrieved_chunks": 0
            }
        
        # Modify question to ask for comparison
        comparison_question = f"Compare and contrast the following papers on this topic: {question}"
        
        answer = await self.llm_service.generate_answer(
            question=comparison_question,
            chunks=all_chunks,
            mode=mode
        )
        
        return {
            "answer": answer,
            "citations": self._build_citations(all_chunks),
            "question": question,
            "mode": mode,
            "retrieved_chunks": len(all_chunks)
        }
