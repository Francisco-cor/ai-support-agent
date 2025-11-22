# Internal AI Support Agent (RAG Architecture)

An enterprise-grade retrieval‑augmented generation (RAG) service
designed to automate internal technical support. It uses lightweight
keyword search plus LLM synthesis to produce deterministic, sourced
answers from internal documentation.

## 🏗 System Architecture & Design

### Core Components

**Ingestion Layer**\
Asynchronous webhook endpoints that accept real‑time document updates.

**Retrieval Engine (SQLite FTS5)**\
- Selected over vector DBs to reduce infra complexity and cost.\
- FTS5 provides high‑precision keyword matching, ideal for technical
docs with exact identifiers and error codes.

**Generative Layer (Google Gemini 2.5 Flash)**\
- High throughput and large context window.\
- Low latency (\~500ms avg).

**API Gateway**\
FastAPI with Pydantic for type safety and auto‑generated Swagger docs.

### Data Flow

    User Query → Sanitization → FTS Retrieval (Top‑K) → Context Assembly → LLM Inference → Response + Citation

## 🚀 Key Features

-   Deterministic RAG with strict context adherence.\
-   Full auditability with source‑linked responses.\
-   Fully containerized, ready for Kubernetes or ECS.\
-   Environment‑based config + strict input validation.

## 🛠️ Local Development Setup

### Prerequisites

-   Python 3.11+
-   Google Cloud Project with Vertex AI / Generative AI enabled

### Installation

``` bash
git clone <repo_url>
cd ai-support-agent
```

**Environment Configuration**

``` bash
cp .env.example .env
```

Add your `GEMINI_API_KEY`.

**Dependencies**

``` bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Database Seeding (ETL)

``` bash
python scripts/seed_docs.py
```

### Run Server

``` bash
uvicorn app.main:app --reload
```

Swagger UI → http://localhost:8000/docs

## 🐳 Docker Production Deployment

``` bash
docker build -t ai-support-agent:latest .
docker run -d -p 8000:8000 --env-file .env --name ai-agent ai-support-agent:latest
```

## 🔌 API Specification

  -------------------------------------------------------------------------------------------------
  Method   Endpoint            Description                 Payload Example
  -------- ------------------- --------------------------- ----------------------------------------
  POST     /api/chat           RAG Inference Endpoint      `{ "query": "How to fix 500 error?" }`

  POST     /api/docs/index     Index new document          `{ "content": "...", "meta": {...} }`

  GET      /api/docs/list      List indexed assets         N/A

  GET      /health             Liveness probe              N/A
  -------------------------------------------------------------------------------------------------

## 🧠 Engineering Decisions & Trade-offs

### Why SQLite FTS Instead of Embeddings?

-   For \<100k docs, TF‑IDF/FTS search beats semantic search for exact
    technical queries (like error codes).
-   Vector DBs introduce infra overhead unnecessary for deterministic
    internal search.

### Why Google Gemini 2.5 Flash?

-   TTFT matters in support workflows.\
-   Flash offers better cost‑performance than GPT‑5 or Claude 4.5 Sonnet
    for pure context‑synthesis tasks.
