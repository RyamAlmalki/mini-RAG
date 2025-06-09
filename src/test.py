import os
from dotenv import load_dotenv
import cohere

# Load the API key from .env file
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Sample text to embed
text = "Hello, I want to test multilingual embeddings."

# Use the multilingual embedding model
EMBEDDING_MODEL_ID = "embed-multilingual-light-v3.0"

response = co.embed(
    texts=[text],
    model=EMBEDDING_MODEL_ID,
    input_type="search_document"  # or "search_query" or "classification" based on your use case
)

embedding = response.embeddings[0]
print(f"Length of embedding: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
