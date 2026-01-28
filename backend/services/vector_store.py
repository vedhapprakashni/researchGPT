"""
Vector Store Service
Manages Pinecone vector database for storing and querying embeddings
"""
import os
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from .embeddings import get_embedding_service


class VectorStore:
    """
    Pinecone vector store for semantic search
    
    Stores document chunks with embeddings and metadata
    for efficient similarity search.
    """
    
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX", "researchgpt")
        self._pc = None
        self._index = None
        self.embedding_service = get_embedding_service()
    
    async def initialize(self):
        """Initialize Pinecone connection and ensure index exists"""
        if not self.api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        self._pc = Pinecone(api_key=self.api_key)
        
        # Check if index exists, create if not
        existing_indexes = [idx.name for idx in self._pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"📝 Creating Pinecone index: {self.index_name}")
            self._pc.create_index(
                name=self.index_name,
                dimension=self.embedding_service.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"✅ Index created: {self.index_name}")
        
        self._index = self._pc.Index(self.index_name)
        print(f"🔗 Connected to Pinecone index: {self.index_name}")
    
    @property
    def index(self):
        """Get Pinecone index"""
        if self._index is None:
            raise RuntimeError("VectorStore not initialized. Call initialize() first.")
        return self._index
    
    async def upsert_chunks(self, chunks: List[Dict], group_id: Optional[str] = None) -> int:
        """
        Store document chunks with their embeddings
        
        Args:
            chunks: List of {chunk_id, paper_id, section, page, text}
            group_id: Optional group ID to associate chunks with
            
        Returns:
            Number of vectors upserted
        """
        if not chunks:
            return 0
        
        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Prepare vectors for Pinecone
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            metadata = {
                "paper_id": chunk["paper_id"],
                "section": chunk["section"],
                "page": chunk["page"],
                "text": chunk["text"][:1000]  # Pinecone metadata limit
            }
            
            # Add group_id if provided
            if group_id:
                metadata["group_id"] = group_id
            
            vectors.append({
                "id": chunk["chunk_id"],
                "values": embedding,
                "metadata": metadata
            })
        
        # Upsert in batches of 100
        batch_size = 100
        total_upserted = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            total_upserted += len(batch)
        
        return total_upserted
    
    async def query(
        self,
        query_text: str,
        top_k: int = 5,
        paper_id: Optional[str] = None,
        group_id: Optional[str] = None,
        paper_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for relevant chunks
        
        Args:
            query_text: Question or search query
            top_k: Number of results to return
            paper_id: Optional filter by single paper
            group_id: Optional filter by group
            paper_ids: Optional filter by list of papers
            
        Returns:
            List of {chunk_id, score, text, section, page, paper_id}
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed_query(query_text)
        
        # Build filter
        filter_dict = None
        if paper_id:
            filter_dict = {"paper_id": {"$eq": paper_id}}
        elif group_id:
            filter_dict = {"group_id": {"$eq": group_id}}
        elif paper_ids:
            filter_dict = {"paper_id": {"$in": paper_ids}}
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        # Format results
        chunks = []
        for match in results.matches:
            chunks.append({
                "chunk_id": match.id,
                "score": match.score,
                "text": match.metadata.get("text", ""),
                "section": match.metadata.get("section", "Unknown"),
                "page": match.metadata.get("page", 0),
                "paper_id": match.metadata.get("paper_id", "")
            })
        
        return chunks
    
    async def delete_paper(self, paper_id: str) -> bool:
        """
        Delete all chunks for a paper
        
        Args:
            paper_id: Paper ID to delete
            
        Returns:
            True if successful
        """
        # Pinecone supports delete by metadata filter
        self.index.delete(filter={"paper_id": {"$eq": paper_id}})
        return True
    
    async def list_papers(self) -> List[str]:
        """
        List all unique paper IDs in the index
        
        Note: This is a workaround since Pinecone doesn't have
        native distinct queries. We use stats for this.
        """
        # Get index stats
        stats = self.index.describe_index_stats()
        
        # This won't give us paper IDs directly, but we track them
        # in our local metadata store (see papers.py router)
        return stats
