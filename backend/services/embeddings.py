"""
Embedding Service
Generates vector embeddings for text chunks using BGE
"""
import os
from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Generate embeddings using BGE (BAAI General Embedding) model
    
    BGE embeddings are optimized for retrieval tasks and provide
    excellent performance for RAG applications.
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the model"""
        if self._model is None:
            print(f"📦 Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            print(f"✅ Embedding model loaded (dim={self._model.get_sentence_embedding_dimension()})")
        return self._model
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector)
        """
        # BGE models work better with query prefix for queries
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 10
        )
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query
        
        For BGE models, queries should be prefixed for better retrieval
        """
        # BGE instruction prefix for queries
        query_with_instruction = f"Represent this sentence for searching relevant passages: {query}"
        return self.embed_text(query_with_instruction)


# Singleton instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
