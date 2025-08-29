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

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Setup Environment Variables

```bash
cp .env.example .env
```

* Open `.env` and set your environment variables (e.g., `OPENAI_API_KEY`).

#### Run the FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

---

### 🔵 Option 2: Run Docker Compose Services

1. Navigate to the docker folder:

```bash
cd docker
```

2. Copy the environment file:

```bash
cp .env.example .env
```

3. Update `.env` with your credentials.

4. Start Docker services:

```bash
sudo docker compose up -d
```
