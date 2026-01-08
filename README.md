# Document Q&A Assistant (RAG)

An AI-powered document question-answering system using Retrieval-Augmented Generation (RAG).

## Features

- Upload PDF, DOCX, TXT, and Markdown documents
- Ask questions based on document content
- Get answers with citations
- Vector-based semantic search
- Local LLM using Ollama (Llama 3.2)

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **LLM**: Ollama (Llama 3.2)
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB
- **Database**: MongoDB Atlas
- **Package Manager**: uv

## Prerequisites

- Python 3.10+
- [uv package manager](https://github.com/astral-sh/uv)
- [Ollama](https://ollama.com/)
- MongoDB Atlas account (free tier)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd document-qa-rag
```

### 2. Install Ollama and pull Llama 3.2

```bash
# Install Ollama (Mac/Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 model
ollama pull llama3.2
```

### 3. Set up MongoDB Atlas

1. Create a free account at https://www.mongodb.com/cloud/atlas
2. Create a free M0 cluster
3. Create database user and whitelist IP (0.0.0.0/0)
4. Get connection string

### 4. Configure Backend

```bash
cd backend
cp .env.example .env
# Edit .env and add your MongoDB URI
uv sync
```

### 5. Configure Frontend

```bash
cd ../frontend
cp .env.example .env
uv sync
```

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
uv run python -m app.main
```

Backend will run on http://localhost:8000

### Start Frontend (Terminal 2)

```bash
cd frontend
uv run streamlit run app.py
```

Frontend will run on http://localhost:8501

## Usage

1. Upload a document (PDF, DOCX, TXT, or MD)
2. Wait for indexing to complete
3. Ask questions about the document
4. View answers with citations

## Project Structure

```
document-qa-rag/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── docs/            # Documentation and diagrams
└── README.md        # This file
```

## Testing

See `docs/test_questions.md` for sample test questions.

## License

MIT

## Author

kaushik maram
