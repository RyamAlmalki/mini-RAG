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
        
        record = None
        async with self.db_client as session:
            async with session.begin():
                list_tbl = sql_text('SELECT * FROM pg_table WHERE tablename = : collection_name')
                result = await session.execute(list_tbl, {'collection_name': collection_name})
                record = result.scalar_one_or_none()
            
        
        return record
    

    async def list_all_collections(self) -> List:
        records = []
        async with self.db_client as session:
            async with session.begin():
                list_tbl = sql_text('SELECT tablename FROM pg_tables WHERE tablename LIKE :prefix')
                result = await session.execute(list_tbl, {'prefix': self.pgvector_table_prefix})
                records = result.scalars().all()
        
        return records
    
    async def get_collection_info(self, collection_name: str) -> dict:
  
        async with self.db_client as session:
            async with session.begin():
                table_info_sql = sql_text('''
                    SELECT schemaname, tablename, 
                    tableowner, tablespace, hasindexes 
                    FROM pg_tables WHERE tablename = :collection_name                       
                ''')
                
                count_sql = sql_text('''
                    SELECT COUNT(*) FROM :collection_name
                ''')

                table_info_result = await session.execute(table_info_sql, {'collection_name': collection_name})
                record_count = await session.execute(count_sql, {'collection_name': collection_name})

                table_data = table_info_result.fetchone()
                if not table_data:
                    return None
                
                count_result = record_count.fetchone()
                if not count_result:
                    return None
                
                return{
                    "table_info": dict(table_data),
                    "record_count": count_result
                }
            
    
    async def delete_collection(self, collection_name: str):
        
        async with self.db_client as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")

                drop_table_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(drop_table_sql)
                await session.commit()
        
        
        return True
    
    async def create_collection(self, collection_name: str,
                                embedding_size: int,
                                do_reset: bool = False):
        
        if do_reset:
            _ = await self.delete_collection(collection_name=collection_name)
        
        is_collection_exists = await self.is_collection_exists(collection_name)
        if not is_collection_exists:
            self.logger.info(f"Creating new PGVector collection: {collection_name}")
            
            async with self.db_client as session:
                async with session.begin():
                    create_table_sql = sql_text(
                        'CREATE TABLE :collection_name (' 
                        f'{PgVectorTableSchemaEnum.ID.value} bigserial PRIMARY KEY'
                        f'{PgVectorTableSchemaEnum.TEXT.value} text, '
                        f'{PgVectorTableSchemaEnum.VECTOR.value} vector({embedding_size}), '
                        f'{PgVectorTableSchemaEnum.CHUNK_ID.value} integer, '
                        f'{PgVectorTableSchemaEnum.METADATA.value} jsonb DEFAULT \'{{}}\',  '
                        f'FOREIGN KEY ({PgVectorTableSchemaEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_table_sql)
                    await session.commit()
            
            return True
        
        return False
                                                
