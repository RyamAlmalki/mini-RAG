#############################
#        APP SETTINGS       #
#############################
APP_NAME="your-app-name"                   # Name of the application
APP_VERSION="0.0.0"                        # Version of the application

# Allowed file types and sizes
FILE_ALLOWED_TYPES=["text/plain","application/pdf"]     # Supported upload types (comma separated list)
FILE_MAX_SIZE=10                                        # Max file size in MB
FILE_DEFAULT_CHUNK_SIZE=512000                          # Default chunk size in bytes

#############################
#     DATABASE SETTINGS     #
#############################
POSTGRES_HOST="your-host"                  # e.g. localhost
POSTGRES_PORT=5432                         # e.g. 5432
POSTGRES_USERNAME="your-username"
POSTGRES_PASSWORD="your-password"
POSTGRES_MAIN_DATABASE="your-database-name"

#############################
#   MODEL / API SETTINGS    #
#############################
GENERATION_BACKEND="your-generation-backend"     # e.g. cohere  | openai
EMBEDDING_BACKEND="your-embedding-backend"       # e.g. cohere  | openai

# API keys / base URLs
OPENAI_API_KEY="your-openai-key"
OPENAI_API_URL="https://api.openai.com/v1"
COHERE_API_KEY="your-cohere-key"

# Generation / Embedding models
GENERATION_MODEL_ID_LITERAL=["model-A","model-B"]        # Available generation models
GENERATION_MODEL_ID="default-generation-model"
EMBEDDING_MODEL_ID="default-embedding-model"
EMBEDDING_MODEL_SIZE=384                                  # Embedding dimension (e.g. 384)

# Defaults for generation
INPUT_DEFAULT_MAX_CHARACTERS=1024
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1

#############################
#   VECTOR STORE SETTINGS   #
#############################
VECTOR_DB_BACKEND_LITERAL=["qdrant","pgvector"]      # Available vector store implementations
VECTOR_DB_BACKEND="pgvector"                         # Selected vector store backend
VECTOR_DB_PATH="path-to-local-qdrant"                # Used only for local qdrant
VECTOR_DB_DISTANCE_METHOD="Cosine"                   # e.g. Cosine / Euclidean
VECTOR_DB_PGVECTOR_INDEX_THRESHOLD=100               # Threshold for creating pgvector index

#############################
#     TEMPLATE SETTINGS     #
#############################
PRIMARY_LANGUAGE="en"
DEFAULT_LANGUAGE="en"
