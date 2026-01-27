"""
Text Chunking Service
Splits text into semantic chunks with overlap for RAG
"""
import tiktoken
from typing import List, Dict
import re


class TextChunker:
    """
    Chunk text into smaller pieces for embedding and retrieval
    
    Uses tiktoken for accurate token counting and preserves:
    - Section boundaries
    - Sentence boundaries where possible
    - Page number metadata
    """
    
    def __init__(
        self,
        chunk_size: int = 600,  # Target tokens per chunk
        chunk_overlap: int = 100,  # Overlap tokens
        model: str = "cl100k_base"  # GPT-4/3.5 tokenizer
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding(model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def chunk_document(
        self,
        sections: List[Dict],
        paper_id: str
    ) -> List[Dict]:
        """
        Chunk a document that's been parsed into sections
        
        Args:
            sections: List of {section, text, page} from PDF parser
            paper_id: Unique identifier for the paper
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        chunk_id = 0
        
        for section_data in sections:
            section_name = section_data["section"]
            text = section_data["text"]
            page = section_data["page"]
            
            # Skip very short sections
            if len(text.strip()) < 50:
                continue
            
            # Chunk this section's text
            section_chunks = self._chunk_text(text, section_name, page)
            
            for chunk_text in section_chunks:
                chunks.append({
                    "chunk_id": f"{paper_id}_chunk_{chunk_id}",
                    "paper_id": paper_id,
                    "section": section_name,
                    "page": page,
                    "text": chunk_text
                })
                chunk_id += 1
        
        return chunks
    
    def _chunk_text(
        self,
        text: str,
        section: str,
        page: int
    ) -> List[str]:
        """
        Split text into chunks of approximately chunk_size tokens
        
        Tries to split on sentence boundaries when possible
        """
        # If text is small enough, return as single chunk
        if self.count_tokens(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []
        
        # Split into sentences
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If single sentence is too long, split it
            if sentence_tokens > self.chunk_size:
                # Save current chunk if not empty
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split long sentence by words
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self.count_tokens(word + ' ')
                    if temp_tokens + word_tokens > self.chunk_size:
                        if temp_chunk:
                            chunks.append(' '.join(temp_chunk))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    current_chunk = temp_chunk
                    current_tokens = temp_tokens
                continue
            
            # Check if adding sentence exceeds chunk size
            if current_tokens + sentence_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + [sentence]
                current_tokens = self.count_tokens(' '.join(current_chunk))
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting on period, question mark, exclamation
        # Preserves abbreviations like "e.g.", "i.e.", "et al."
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap(self, chunk: List[str]) -> List[str]:
        """Get overlap sentences from end of chunk"""
        if not chunk:
            return []
        
        overlap = []
        tokens = 0
        
        # Work backwards through sentences
        for sentence in reversed(chunk):
            sentence_tokens = self.count_tokens(sentence)
            if tokens + sentence_tokens > self.chunk_overlap:
                break
            overlap.insert(0, sentence)
            tokens += sentence_tokens
        
        return overlap
