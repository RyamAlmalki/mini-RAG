from fastapi import FastAPI
from routes import base, data, nlp
from helper.config import get_settings
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker



@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    
    app.db_engine = create_async_engine(
        postgres_conn,
    )
    
    app.db_client = sessionmaker(
        bind=app.db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
 

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

    app.vector_db_client = await vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    
    # Now this is safe, the instance is returned and connected (or connect called explicitly)
    await app.vector_db_client.connect()
    
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE
    )
    
    yield

    print("Shutting down MongoDB client")
    app.db_engine.dispose()
    await app.vector_db_client.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(base.router, prefix="/v1/base", tags=["base"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])
app.include_router(nlp.router, prefix="/v1/nlp", tags=["nlp"])