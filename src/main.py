from fastapi import FastAPI
from routes import base, data

app = FastAPI()

app.include_router(base.router, prefix="/v1/base", tags=["base"])

app.include_router(data.router, prefix="/v1/data", tags=["data"])