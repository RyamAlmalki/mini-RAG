from fastapi import FastAPI
from routes import base, data
# motor is like a wrapper for pymongo, but for async
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
import logging

logging.getLogger("pymongo").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.DEBUG,  # Show all levels: DEBUG and above
    format="%(levelname)s:%(name)s:%(message)s"
)

# The Problem: Where Do You Connect to the Database?
# Connect to the database when the app starts

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()  # get MongoDB connection info
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)  # connect to Mongo
    app.db_client = app.mongo_conn[settings.MONGODB_DB_NAME]  # get the actual database
    print("MongoDB client started")  # (just for logging/debugging)

    llm_provider_factory = LLMProviderFactory(settings)
    
    # Generation client
    app.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
    
    # can be changed during runtime
    app.generation_client.set_generation_model(
        settings.GENERATION_MODEL_ID,
    )

    # Embedding client
    app.embedding_client = llm_provider_factory.create(settings.EMBEDDING_BACKEND)
    
    # can be changed during runtime
    app.embedding_client.set_embedding_model(
        settings.EMBEDDING_MODEL_ID,
        settings.EMBEDDING_SIZE
    )

    yield  # <--- the app runs during this time

    print("Shutting down MongoDB client")
    app.mongo_conn.close()  # cleanly disconnect from Mongo


app = FastAPI(lifespan=lifespan)


app.include_router(base.router, prefix="/v1/base", tags=["base"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])