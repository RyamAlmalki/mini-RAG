FROM ghcr.io/astral-sh/uv:0.8.11 

WORKDIR /app

# Install additional system dependencies for 1xml and other packages
RUN apt-get update && apt-get install -y \
    build-essential \ 
    libavif-dev pkg-config \ 
    libjpeg-dev \
    gcc unzip zip \ 
    python3-dev \ 
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \ 
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY src/ .

RUN mkdir -p models/db_schema/minirag

COPY docker/minirag/alembic.ini /app/models/db_schema/minirag/

RUN alembic upgrade head