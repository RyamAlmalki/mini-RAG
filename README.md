## 👋🏻 Introduction

This is a minimal implementation of the RAG model for question answering.

---

## 🔹 Endpoints Overview

| **Method** | **Endpoint** | **Body Parameters** | **Purpose** |
|------------|--------------|----------------------|-------------|
| POST | `/v1/data/upload/{project_id}` | `file` (UploadFile, allowed types: `text/plain`, `application/pdf`) | Upload a raw file (PDF or text) and store it in the system for further processing. |
| POST | `/v1/data/process/{project_id}` | `file_id` (str, optional)<br>`chunk_size` (int, default=100)<br>`chunk_overlap` (int, default=20)<br>`do_reset` (int, default=0) | Split the uploaded file into text chunks for NLP, controlling chunk size and overlap. |
| POST | `/v1/nlp/index/push/{project_id}` | `do_reset` (int, default=0) | Insert the processed chunks into the vector database (for semantic search/QA). |
| GET  | `/v1/nlp/index/info/{project_id}` | *(no body)* | Retrieve metadata about the project’s NLP index (e.g. stats, collection status). |
| GET  | `/v1/nlp/index/search/{project_id}` | `text` (str)<br>`limit` (int, default=5) | Search the indexed project data using semantic similarity (returns relevant chunks). |
| GET  | `/v1/nlp/index/answer/{project_id}` | `text` (str)<br>`limit` (int, default=5) | Perform Retrieval-Augmented Generation (RAG): retrieves relevant chunks and generates a natural language answer with context. |

---

## 🚀 Getting Started

### 🟢 Option 1: Run with MiniConda

* Python 3.8 or later

#### Install Python using MiniConda

1. Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)

2. Create a new environment:

```bash
conda create -n mini-rag python=3.8
```

3. Activate the environment:

```bash
conda activate mini-rag
```

4. Activate the environment:

```bash
cd src
```

5. Install Dependencies:

```bash
pip install -r requirements.txt
```

6. Setup Environment Variables

```bash
cp .env.example .env
```

* Open `.env` and set your environment variables (e.g., `OPENAI_API_KEY`).


7. Run Alembic Migration

```bash
cp .env.example .env
```

8. Run the FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

### 🔵 Option 2: Run Docker Compose Services

1. Create all required .env files from examples:

```bash
cd docker/env
cp .env.example.app .env.app
cp .env.example.postgres .env.postgres
cp .env.example.grafana .env.grafana
cp .env.example.postgres-exporter .env.postgres-exporter
```

2. Setup the Alembic configuration for the FastAPI application

```bash
cd ..
cd docker/minirag
cp alembic.example.ini alembic.ini
```

3. Start the services

```bash
cd docker
docker compose up --build -d
```
