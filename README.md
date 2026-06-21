# RAG-REDIS-QDRANT

A high-performance **Retrieval-Augmented Generation (RAG)** pipeline that extracts text from PDF documents, stores vector embeddings in **Qdrant**, and generates answers via **Groq**. Designed to be extended with **Redis** as a semantic cache layer to reduce redundant LLM calls, lower latency, and cut cost.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Qdrant Setup](#qdrant-setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

This project answers natural-language questions about the content of a PDF document. It works by:

1. Extracting and chunking text from a PDF at startup
2. Embedding each chunk with a local sentence-transformer model
3. Storing embeddings in a Qdrant vector database (local Docker or cloud)
4. At query time, embedding the user question and retrieving the most semantically similar chunks
5. Passing retrieved context to a Groq-hosted LLM to generate a grounded, factual answer

The pipeline runs fully in a terminal REPL — type a question, get an answer based strictly on the document.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                              │
│                                                                  │
│  ┌──────────┐    ┌───────────┐    ┌─────────────────────────┐   │
│  │  PDF     │───▶│  PyMuPDF  │───▶│  Text Chunker           │   │
│  │ Document │    │ Extractor │    │  (500-char windows)     │   │
│  └──────────┘    └───────────┘    └────────────┬────────────┘   │
│                                                │                 │
│                                                ▼                 │
│                                   ┌─────────────────────────┐   │
│                                   │  SentenceTransformer    │   │
│                                   │  all-MiniLM-L6-v2       │   │
│                                   │  (384-dim embeddings)   │   │
│                                   └────────────┬────────────┘   │
│                                                │                 │
│                                                ▼                 │
│                                   ┌─────────────────────────┐   │
│                                   │       Qdrant            │   │
│                                   │  Vector Store (cosine)  │   │
│                                   └────────────┬────────────┘   │
│                                                │                 │
│  User Query ─────────────────────────────────▶│                 │
│       │                                        │ top-k chunks    │
│       │ embed                                  ▼                 │
│       └──────────────────────────▶  ┌──────────────────────┐   │
│                                      │   Groq LLM           │   │
│                                      │ (context + question) │   │
│                                      └──────────┬───────────┘   │
│                                                 │                │
│                                                 ▼                │
│                                          Answer to User          │
└──────────────────────────────────────────────────────────────────┘
```

> **Planned:** Redis semantic cache sits between the user query and Qdrant/Groq, returning cached answers for near-duplicate questions to skip embedding + LLM calls entirely.

---

## Tech Stack

| Component | Library / Service |
|---|---|
| PDF parsing | [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) |
| Embeddings | [sentence-transformers](https://www.sbert.net/) — `all-MiniLM-L6-v2` (384 dims) |
| Vector database | [Qdrant](https://qdrant.tech/) (local Docker or Qdrant Cloud) |
| LLM inference | [Groq](https://groq.com/) API |
| Semantic cache (planned) | [Redis](https://redis.io/) |
| Environment config | [python-dotenv](https://github.com/theskumar/python-dotenv) |

---

## Project Structure

```
RAG-REDIS-QDRANT/
├── RAG_MAIN.py          # Entry point — pipeline orchestration and REPL
├── groq_client.py       # Groq API wrapper for LLM answer generation
├── qdrantClient.py      # Qdrant cloud connection helper / diagnostics
├── requirements.txt     # Python dependencies
├── .env                 # API keys (never commit — gitignored)
├── .gitignore
└── LICENSE
```

### File Roles

**[RAG_MAIN.py](RAG_MAIN.py)** — Core pipeline. Handles PDF text extraction, chunking, embedding, Qdrant collection setup, vector upsert, and the interactive query loop.

**[groq_client.py](groq_client.py)** — Wraps the Groq SDK. Takes retrieved context chunks and the user's question, calls the LLM, and returns the generated answer string.

**[qdrantClient.py](qdrantClient.py)** — Standalone Qdrant cloud client used for diagnostics (e.g. listing collections). The main pipeline uses a local client configured in `RAG_MAIN.py`.

---

## Prerequisites

- Python 3.9+
- Docker (for local Qdrant) — or a Qdrant Cloud account
- A [Groq API key](https://console.groq.com/)

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/abdulsamadgilal/RAG-REDIS-QDRANT.git
cd RAG-REDIS-QDRANT

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

> `sentence-transformers` will download the `all-MiniLM-L6-v2` model (~80 MB) on first run. It is cached locally afterward.

---

## Configuration

Create a `.env` file in the project root (copy the template below — never commit real keys):

```env
GROQ_API_KEY=your_groq_api_key_here
QDRANT_API_KEY=your_qdrant_cloud_api_key_here          # only needed for cloud
QDRANT_CLUSTER_ENDPOINT=https://your-cluster.qdrant.io # only needed for cloud
```

The `.env` file is listed in `.gitignore` and will not be committed to version control.

---

## Qdrant Setup

### Option A — Local Docker (default)

The pipeline in `RAG_MAIN.py` points to `http://localhost:6333` by default.

```bash
# Pull and run Qdrant
docker pull qdrant/qdrant
docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

Qdrant dashboard will be available at `http://localhost:6333/dashboard`.

### Option B — Qdrant Cloud

1. Create a free cluster at [cloud.qdrant.io](https://cloud.qdrant.io/)
2. Copy your cluster URL and API key into `.env`
3. Update the client in `RAG_MAIN.py`:

```python
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_CLUSTER_ENDPOINT"),
    api_key=os.getenv("QDRANT_API_KEY")
)
```

---

## Usage

1. Place your PDF in the project root and update `PDF_PATH` in `RAG_MAIN.py`:

```python
PDF_PATH = "your_document.pdf"
```

2. Start Qdrant (Docker or cloud — see above).

3. Run the pipeline:

```bash
python RAG_MAIN.py
```

On first run the collection is created and all chunks are indexed. Subsequent runs skip indexing and go straight to the query loop.

```
Collection 'pdf_docs' created and indexed.
Stored 42 chunks.

Ask anything about the document. Type 'exit' to quit.

You: What are the key skills listed?
Assistant: Based on the document, the key skills include ...

You: exit
Goodbye!
```

---

## How It Works

### 1. PDF Extraction (`extract_chunks`)

PyMuPDF reads each page and extracts raw text. The text is split into overlapping 500-character chunks, stripping whitespace. Smaller chunks improve retrieval precision; larger chunks preserve more context per result.

### 2. Collection Bootstrap (`setup_collection`)

On startup, the pipeline checks whether the Qdrant collection `pdf_docs` exists. If not, it creates a collection configured for **cosine similarity** over **384-dimensional** vectors, extracts and embeds all chunks, then upserts them as `PointStruct` objects with the raw text stored in the payload.

### 3. Embedding (`store_chunks`)

`SentenceTransformer("all-MiniLM-L6-v2")` converts each text chunk into a 384-dim float vector. This model is fast, lightweight, and runs entirely on CPU — no GPU required.

### 4. Semantic Search (`search`)

The user's query is encoded with the same model. Qdrant performs an approximate nearest-neighbor search using cosine distance and returns the `top_k` (default 3) most relevant chunks.

### 5. LLM Answer Generation (`search_and_answer`)

The retrieved chunks are joined into a context block and sent to Groq along with the original question. The system prompt constrains the LLM to answer **only** from the provided context, preventing hallucination outside the document.

---

## Roadmap

- [ ] **Redis semantic cache** — Cache question embeddings and their answers in Redis. On each query, check for a semantically similar cached question (cosine similarity above a threshold) before hitting Qdrant and Groq. Reduces latency and API cost for repeated or near-duplicate queries.
- [ ] **Multi-document support** — Index multiple PDFs into a single collection with per-document metadata filtering.
- [ ] **Streaming responses** — Use Groq's streaming API for token-by-token output in the terminal.
- [ ] **Web UI** — FastAPI + simple frontend for browser-based document Q&A.
- [ ] **Configurable chunking** — Support overlap windows and sentence-boundary-aware splitting.

---

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
