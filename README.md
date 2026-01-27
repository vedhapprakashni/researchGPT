# ResearchGPT

AI-powered Research Paper Assistant using RAG (Retrieval-Augmented Generation).

## Features

- 📄 Upload research papers (PDF)
- 💬 Ask questions about your papers
- 🎯 Get accurate, context-grounded answers
- 📍 Responses include page citations

## Quick Start

### Backend

```bash
cd d:\researchgpt
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

- **Backend**: FastAPI + Python
- **LLM**: Groq (LLaMA)
- **Embeddings**: BGE (sentence-transformers)
- **Vector DB**: Pinecone
- **Frontend**: React + Next.js
