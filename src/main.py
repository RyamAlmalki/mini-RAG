from fastapi import FastAPI
from routes import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from helper.config import get_settings
from contextlib import asynccontextmanager


# The Problem: Where Do You Connect to the Database?
# Connect to the database when the app starts

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()  # get MongoDB connection info
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)  # connect to Mongo
    app.db_client = app.mongo_conn[settings.MONGODB_DB_NAME]  # get the actual database
    print("MongoDB client started")  # (just for logging/debugging)

    yield  # <--- the app runs during this time

    print("Shutting down MongoDB client")
    app.mongo_conn.close()  # cleanly disconnect from Mongo

app = FastAPI(lifespan=lifespan)


app.include_router(base.router, prefix="/v1/base", tags=["base"])
app.include_router(data.router, prefix="/v1/data", tags=["data"])