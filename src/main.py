from fastapi import FastAPI
from routes import base, data, nlp
from helper.config import get_settings
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from utils.metrics import setup_metrics


# Define an asynchronous lifespan context manager for app startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load settings from environment or configuration
    settings = get_settings()
    
    # Construct Postgres connection string
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    
    # Create an asynchronous SQLAlchemy engine
    app.db_engine = create_async_engine(
        postgres_conn,
    )
    
    # Create a session factory for async DB sessions
    app.db_client = sessionmaker(
        bind=app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Prevent automatic expiration of objects after commit
    )
 
    # Initialize Language Model (LLM) provider factory
    llm_provider_factory = LLMProviderFactory(settings)

    # Initialize Vector Database provider factory with app's DB client
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # Create a client for text generation LLM and set the model
    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    # Create a client for embedding generation LLM and set the model & size
    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

    # Create and connect the vector database client
    app.vector_db_client = await vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()
    
    # Initialize template parser for handling multi-language templates
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
    )
    
    # Yield control to FastAPI while app runs
    yield

    # Cleanup on shutdown: dispose DB engine and disconnect vector DB
    app.db_engine.dispose()
    await app.vector_db_client.disconnect()


# Create FastAPI app instance with custom lifespan
app = FastAPI(lifespan=lifespan)

# Setup monitoring metrics for the app
setup_metrics(app)

# Include routers for different API endpoints
app.include_router(base.router, prefix="/v1/base", tags=["base"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])
app.include_router(nlp.router, prefix="/v1/nlp", tags=["nlp"])
