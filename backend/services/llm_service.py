"""
LLM Service
Handles communication with Groq API for LLaMA inference
"""
import os
from typing import Optional
from groq import Groq
from ..prompts.templates import SYSTEM_PROMPT, build_prompt


class LLMService:
    """
    LLM service using Groq API for fast LLaMA inference
    
    Groq provides extremely fast inference times for LLaMA models,
    making it ideal for interactive Q&A applications.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self._client = None
        # Use LLaMA 3.3 70B (current model on Groq)
        self.model = "llama-3.3-70b-versatile"
    
    @property
    def client(self) -> Groq:
        """Lazy load Groq client"""
        if self._client is None:
            if not self.api_key:
                raise ValueError("GROQ_API_KEY environment variable not set")
            self._client = Groq(api_key=self.api_key)
        return self._client
    
    async def generate_answer(
        self,
        question: str,
        chunks: list,
        mode: str = "academic",
        max_tokens: int = 1024,
        temperature: float = 0.3
    ) -> str:
        """
        Generate an answer using RAG context
        
        Args:
            question: User's question
            chunks: Retrieved context chunks from vector store
            mode: Response mode (academic, simple, eli5)
            max_tokens: Maximum tokens in response
            temperature: Creativity (lower = more focused)
            
        Returns:
            Generated answer text
        """
        # Build the prompt with context
        user_prompt = build_prompt(question, chunks, mode)
        
        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def generate_summary(
        self,
        text: str,
        max_tokens: int = 500
    ) -> str:
        """
        Generate a summary of text
        
        Useful for summarizing paper abstracts or sections
        """
        prompt = f"""Summarize the following academic text in a clear, concise way:

{text}

Summary:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at summarizing academic papers. Be concise but capture key points."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        return response.choices[0].message.content


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
