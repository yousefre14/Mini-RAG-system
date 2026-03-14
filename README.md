# Mini-RAG-system
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=flat&logo=mongodb&logoColor=white)](https://mongodb.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

A modular **Retrieval-Augmented Generation (RAG) backend** built with FastAPI, MongoDB, LangChain loaders/splitters, pluggable LLM providers, and a vector database layer.

This project is designed to show a complete RAG pipeline—from document ingestion to semantic retrieval—with a clean separation between API routes, controllers, models, and provider factories.

---

## Why this project stands out

- **End-to-end RAG workflow**: upload documents, process/chunk text, index embeddings, and run semantic search.  
- **Pluggable architecture**: both LLM and vector DB clients are created through provider factories.  
- **Production-oriented structure**: explicit routes, controller layer, data models, and environment-based config.  
- **Async-first API layer**: FastAPI + async MongoDB driver (`motor`) for scalable I/O handling.

---

## Architecture overview

```text
Client
  ↓
FastAPI Routes
  ├─ /api/v1/data  (upload + processing)
  └─ /api/v1/nlp   (indexing + retrieval)
  ↓
Controllers
  ├─ Data/Project/Process Controllers
  └─ NLP Controller
  ↓
Storage + AI Backends
  ├─ MongoDB (projects, assets, chunks metadata)
  ├─ Vector DB (Qdrant provider)
  └─ LLM Providers (OpenAI / Cohere)
```

### Request lifecycle (pipeline)

1. **Upload file** to a project (`/api/v1/data/upload/{project_id}`).  
2. **Process file** into chunks using LangChain loaders + splitters (`/api/v1/data/process/{project_id}`).  
3. **Push chunks to vector DB** by embedding and indexing (`/api/v1/nlp/index/push/{project_id}`).  
4. **Search semantically** over indexed chunks (`/api/v1/nlp/index/search/{project_id}`).

---

## Tech stack

- **Backend**: FastAPI, Uvicorn
- **Data**: MongoDB (Motor async driver)
- **RAG processing**: LangChain, PyMuPDF, RecursiveCharacterTextSplitter
- **LLM/Embeddings providers**: OpenAI, Cohere
- **Vector DB**: Qdrant client

---

## Repository structure

```text
src/
  main.py                       # App startup/shutdown + dependency wiring
  routes/
    base.py                     # Welcome route
    data.py                     # Upload + process routes
    nlp.py                      # Index + search routes
    schemas/                    # Pydantic request schemas
  controllers/
    Data_Controller.py
    ProjectController.py
    ProcessController.py        # File loading + chunking
    nlp_controller.py           # Embedding/index/search orchestration
  stores/
    llm/                        # LLM provider interfaces + factory
    vectordb/                   # Vector DB interfaces + factory
  models/                       # DB schemas + models
  assets/
    files/                      # Stored uploaded files
    vectordb/                   # Local vector DB data
docker/
  docker-compose.yml            # MongoDB service
```

---

## Prerequisites

- Python 3.8+
- pip
- Docker + Docker Compose (recommended for MongoDB)

---

## Quick start

### 1) Clone and enter the repo

```bash
git clone <your-repo-url>
cd Mini-RAG-system
```

### 2) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

> Note: the dependency file in this repo is currently named `requirments.txt`.

```bash
pip install -r requirments.txt
```

### 4) Start MongoDB (Docker)

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 5) Configure environment variables

Create a `.env` file in the project root:

```env
APP_NAME=Mini-RAG-system
APP_VERSION=1.0.0

FILE_ALLOWED_TYPES=["application/pdf","text/plain"]
FILE_MAX_SIZE=10485760
FILE_DEFAULT_CHUNK_SIZE=1048576

MongoDB_URI=mongodb://<username>:<password>@localhost:27017
MongoDB_DATABASE=mini_rag

GENERATION_BACKEND=openai
EMBEDDING_BACKEND=openai

OPENAI_API_KEY=your_openai_key
OPENAI_API_URL=
COHERE_API_KEY=

GENERATION_MODEL_ID=gpt-4o-mini
EMBEDDING_MODEL_ID=text-embedding-3-small
EMBEDDING_MODEL_SIZE=1536
INPUT_DAFAULT_MAX_CHARACTERS=4000
GENERATION_DAFAULT_MAX_TOKENS=500
GENERATION_DAFAULT_TEMPERATURE=0.2

VECTOR_DB_BACKEND=qdrant
VECTOR_DB_PATH=src/assets/vectordb/qdrant_db
VECTOR_DB_DISTANCE_METHOD=Cosine
VECTOR_DB_MODEL_ID=mini-rag
```

### 6) Run the API

```bash
python -m uvicorn src.main:app --reload --reload-dir src
```

Open API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`

---

## API workflow examples

### 1) Health / welcome

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/"
```

### 2) Upload a document

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/upload/demo-project" \
  -F "file=@/absolute/path/to/document.pdf"
```

### 3) Process document into chunks

Use the uploaded filename as `file_id`.

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/data/process/demo-project" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "document.pdf",
    "chunk_size": 500,
    "overlap_size": 50,
    "do_reset": 0
  }'
```

### 4) Push chunks into vector index

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlp/index/push/demo-project" \
  -H "Content-Type: application/json" \
  -d '{"do_reset": 1}'
```

### 5) Run semantic search

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/nlp/index/search/demo-project" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Summarize the key objectives",
    "limit": 5
  }'
```

---

## Core capabilities demonstrated

- **Project-based document isolation** (separate collections/files per project).
- **Multi-format ingestion** (TXT and PDF loaders).
- **Chunking with overlap** for context-preserving retrieval.
- **Embedding + indexing pipeline** with configurable providers.
- **Semantic retrieval** from a vector store.
- **Factory-driven backend abstraction** for easier provider swapping.

---

## Roadmap ideas

- Add reranking and hybrid (keyword + vector) search.
- Add answer generation endpoint (RAG QA response).
- Add authentication and role-based project access.
- Add CI checks + API integration tests.
- Containerize full stack (API + MongoDB + vector store) for one-command boot.

---

## License

Add your preferred license file (`MIT`, `Apache-2.0`, etc.) to clarify usage for companies and contributors.
