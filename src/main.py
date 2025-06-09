from fastapi import FastAPI
from routes import base, data, nlp
# motor is like a wrapper for pymongo, but for async
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from contextlib import asynccontextmanager

from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
import logging

logging.getLogger("pymongo").setLevel(logging.WARNING)

# logging.basicConfig(
#     level=logging.DEBUG,  # Show all levels: DEBUG and above
#     format="%(levelname)s:%(name)s:%(message)s"
# )

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    app.db_client = app.mongo_conn[settings.MONGODB_DB_NAME]
    print("MongoDB client started")

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(settings)

    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

    # <-- FIXED: Await here
    app.vector_db_client = await vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    
    # Now this is safe, the instance is returned and connected (or connect called explicitly)
    await app.vector_db_client.connect()
    
    yield

    print("Shutting down MongoDB client")
    app.mongo_conn.close()
    await app.vector_db_client.disconnect()


app = FastAPI(lifespan=lifespan)


app.include_router(base.router, prefix="/v1/base", tags=["base"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])
app.include_router(nlp.router, prefix="/v1/nlp", tags=["nlp"])