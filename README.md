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

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT / POSTMAN                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP
┌─────────────────────────▼───────────────────────────────────┐
│                   FastAPI REST API                          │
│          /upload  /process  /index  /search  /answer        │
└────┬──────────────┬──────────────────────┬──────────────────┘
     │              │                      │
┌────▼────┐  ┌──────▼──────┐      ┌────────▼────────┐
│  File   │  │   Data      │      │   RAG Query     │
│ Upload  │  │  Pipeline   │      │    Engine       │
│ Handler │  │ (Chunking)  │      │                 │
└────┬────┘  └──────┬──────┘      └────────┬────────┘
     │              │                      │
     │       ┌──────▼──────┐      ┌────────▼────────┐
     │       │  LLM Factory│      │  VectorDB       │
     │       │  Interface  │      │  Factory        │
     │       │             │      │  Interface      │
     │       │ ┌─────────┐ │      │ ┌─────────────┐ │
     │       │ │ OpenAI  │ │      │ │   ChromaDB  │ │
     │       │ │ Ollama  │ │      │ │   Qdrant    │ │
     │       │ │ ...     │ │      │ │   ...       │ │
     │       │ └─────────┘ │      │ └─────────────┘ │
     │       └─────────────┘      └─────────────────┘
     │
┌────▼────────────────────────────────────────────────┐
│                   MongoDB (Motor)                    │
│         Projects │ Files │ Chunks │ Indexes          │
└──────────────────────────────────────────────────────┘
     All services containerized via Docker Compose
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

```
Mini-RAG-system/
│
├── src/
│   ├── models/              # MongoDB schemas & data models
│   ├── controllers/         # Route handlers (upload, process, search)
│   ├── helpers/
│   │   ├── llm/
│   │   │   ├── LLMInterface.py      # Abstract LLM contract
│   │   │   ├── LLMFactory.py        # Provider resolver
│   │   │   ├── providers/
│   │   │   │   ├── OpenAIProvider.py
│   │   │   │   └── OllamaProvider.py
│   │   └── vectordb/
│   │       ├── VectorDBInterface.py  # Abstract VectorDB contract
│   │       ├── VectorDBFactory.py    # Engine resolver
│   │       └── providers/
│   │           ├── ChromaDBProvider.py
│   │           └── QdrantProvider.py
│   ├── routes/              # FastAPI route definitions
│   └── main.py              # App entrypoint
│
├── docker/
│   ├── docker-compose.yml   # MongoDB + App orchestration
│   └── .env.example
│
├── .env                     # Environment variables
├── requirements.txt
└── README.md
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
