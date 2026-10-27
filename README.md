# GroundTrace: Enterprise RAG & Context Engineering Platform with FastEmbed

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)

**GroundTrace** is a high-performance Enterprise Retrieval-Augmented Generation (RAG) and Distributed Microservices Log Telemetry Platform. It combines FastEmbed dense vector generation, in-memory vector index storage with cosine similarity search, context engineering with strict source citations, and automated microservice log troubleshooting with error code catalog mapping.

---

## 🏛 System Architecture

```
+-------------------------------------------------------------------------------+
|                             Ingestion Pipeline                                |
|  Technical Docs / Schemas / Logs  -->  Semantic Chunker  -->  Dense Embedder  |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       In-Memory Vector Store & Index                          |
|         Cosine Similarity | Top-K Retrieval | Metadata Filtering              |
+---------------------------------------+---------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|   Enterprise Knowledge RAG      |           |  Microservice Log Diagnostics   |
| - Context Engineering Block     |           | - Regex Telemetry Normalization |
| - Strict Attribution Citations  |           | - Trace ID & Error Code Mapping |
| - Faithfulness & Grounding Eval |           | - Root Cause & Remediation      |
+---------------------------------+           +---------------------------------+
                 |                                             |
                 +----------------------+----------------------+
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                       LLMOps Telemetry & Observability                        |
|   Faithfulness (96%) | Relevance (91%) | Latency (ms) | Token Accounting & $  |
+-------------------------------------------------------------------------------+
```

---

## ✨ Core Engineering Capabilities

1. **FastEmbed & In-Memory Vector Indexing**:
   - Computes L2-normalized dense embeddings with multi-gram hashing and term projection.
   - In-memory vector store supporting cosine similarity ranking, top-k retrieval, threshold score filtering, and metadata separation.

2. **Context Engineering & Grounding Citations**:
   - Recursive character chunker with sentence and paragraph boundary awareness.
   - Context compression and prompt framing injecting retrieved context items with explicit inline citations (`[Doc: ... | Chunk #...]`).
   - Factual grounding and anti-hallucination verification comparing generated claims against source chunks.

3. **Microservices Log Diagnostics & Error Code Mapping**:
   - Real-time extraction and normalization of distributed telemetry: Timestamp, Log Level, Service Name, Trace ID, and Error Code.
   - Catalog-driven error resolution mapping production incidents (e.g. `ERR_PG_CONN_TIMEOUT`, `ERR_K8S_OOMKILLED`, `ERR_REDIS_CONN_REFUSED`) to actionable root cause analyses and engineering remediation steps.

4. **LLMOps Quality & Observability Metrics**:
   - **Faithfulness Score**: Quantifies the percentage of claims supported by verified retrieved chunks.
   - **Context Relevance Score**: Measures alignment between the user's query and retrieved context chunks.
   - **Latency Decomposition**: Profiling across embedding, retrieval, and synthesis phases.
   - **Cost Estimator**: Accurate token accounting and cost tracking.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12, FastAPI, Pydantic v2, Uvicorn, Pytest
- **Frontend / Dashboard**: Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons
- **DevOps**: Docker, Docker Compose, Vercel

---

## 🚀 Getting Started

### Local Setup (Backend)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated test suite
pytest tests -v

# Run FastAPI server
uvicorn main:app --reload --port 8001
```

Interactive Swagger docs available at `http://localhost:8001/docs`.

### Local Setup (Frontend)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Open `http://localhost:3000` (or `http://localhost:3001` if running alongside AgentForge).

---

## 🧪 Automated Testing

GroundTrace includes a comprehensive pytest suite covering chunking, embeddings, vector indexing, context synthesis, log diagnostics, and faithfulness scoring:

```bash
pytest backend/tests/test_groundtrace.py -v
```

---

## 📄 License

This project is licensed under the MIT License.
