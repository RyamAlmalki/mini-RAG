# 👋🏻 Introduction

This is a minimal implementation of the RAG model for question answering.

## 🚀 Getting Started

You can run this project in **two ways**:

* **Option 1: Using MiniConda (recommended for local development)**
* **Option 2: Using Docker Compose (recommended for deployment / containerized setup)**

---

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
