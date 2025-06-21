from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import (PgVectorTableSchemaEnum, 
                            PgVectorDistanceMethodEnum, 
                            PgVectorIndexTypeEnum)
import logging
from typing import List
from models.db_schemes import RetrievedDocuments
from sqlalchemy.sql import text as sql_text
import json 


class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, 
                 distance_method: str = None, 
                 default_vector_size: int = 786):
        
        self.db_client = db_client
        self.distance_method = distance_method
        self.default_vector_size = default_vector_size

        self.pgvector_table_prefix = PgVectorTableSchemaEnum._PREFIX.value

        self.logger = logging.getLogger("Uvicorn")

        if distance_method == PgVectorDistanceMethodEnum.COSINE.value:
            self.distance_method = PgVectorDistanceMethodEnum.COSINE.value
        elif distance_method == PgVectorDistanceMethodEnum.DOT.value:
            self.distance_method = PgVectorDistanceMethodEnum.DOT.value
        

    async def connect(self):
        # tell postgres to create extension pgvector
        async with self.db_client as session:
            async with session.begin():
                await session.execute(
                    sql_text("CREATE EXTENSION IF NOT EXISTS vector;")
                )
            await session.commit()
            
    async def disconnect(self):
        pass

    async def is_collection_exists(self, collection_name: str) -> bool:
        async with self.db_client as session:
            async with session.begin():
                list_tbl = sql_text('SELECT * FROM pg_table WHERE tablename = : collection_name')
                result = await session.execute(list_tbl, {'collection_name': collection_name})