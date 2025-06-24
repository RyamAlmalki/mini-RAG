from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnum import (PgVectorTableSchemaEnum, 
                            PgVectorDistanceMethodEnum, 
                            PgVectorIndexTypeEnum)
import logging
from typing import List
from models.db_schemes import RetrievedDocuments
from sqlalchemy.sql import text as sql_text



class PGVectorProvider(VectorDBInterface):
    def __init__(self, db_client, 
                 distance_method: str = None, 
                 default_vector_size: int = 786, index_threshold: int = 100):
        
        self.db_client = db_client
        self.distance_method = distance_method
        self.default_vector_size = default_vector_size
        self.index_threshold = index_threshold

        self.pgvector_table_prefix = PgVectorTableSchemaEnum._PREFIX.value

        self.logger = logging.getLogger("Uvicorn")

        self.default_index_name = lambda collection_name: f"{self.pgvector_table_prefix}_{collection_name}_index"
        
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

        is_collection_existed = await self.is_collection_existed(collection_name=collection_name)
        if not is_collection_existed:
            self.logger.info(f"Creating collection: {collection_name}")
            async with self.db_client() as session:
                async with session.begin():
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableSchemaEnum.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableSchemaEnum.TEXT.value} text, '
                            f'{PgVectorTableSchemaEnum.VECTOR.value} vector({embedding_size}), '
                            f'{PgVectorTableSchemaEnum.METADATA.value} jsonb DEFAULT \'{{}}\', '
                            f'{PgVectorTableSchemaEnum.CHUNK_ID.value} integer, '
                            f'FOREIGN KEY ({PgVectorTableSchemaEnum.CHUNK_ID.value}) REFERENCES chunks(chunk_id)'
                        ')'
                    )
                    await session.execute(create_sql)
                    await session.commit()
            
            return True

        return False



    async def is_index_existed(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client as session:
            async with session.begin():
                
                index_sql = sql_text(
                    'SELECT 1 FROM pg_indexes WHERE tablename = :collection_name AND indexname = :index_name'
                )
                
                result = await session.execute(index_sql, {
                    'collection_name': collection_name,
                    'index_name': index_name
                })
                
                return bool(result.scalar_one_or_none())


    async def create_vector_index(self, collection_name: str,
                                  index_type: str = PgVectorIndexTypeEnum.HNSW.value,):
        
        is_index_existed = await self.is_index_existed(collection_name=collection_name)

        if is_index_existed:
            return False
        
        async with self.db_client as session:
            async with session.begin():
                count_sql = sql_text(
                    f'SELECT COUNT(*) FROM {collection_name}'
                )
                result = await session.execute(count_sql)
                record_count = result.scalar_one()

                if record_count < self.index_threshold:
                    self.logger.info(f"Collection {collection_name} has only {record_count} records, skipping index creation.")
                    return False

                self.logger.info(f"Creating index for collection: {collection_name} with type: {index_type}")
                
                index_name = self.default_index_name(collection_name)
                create_index_sql = sql_text(
                    f'CREATE INDEX {index_name} '
                    f'ON {collection_name} USING {index_type} '
                    f'({PgVectorTableSchemaEnum.VECTOR.value} {self.distance_method})'
                )
                
                await session.execute(create_index_sql)
                await session.commit()


    

    async def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict = None, record_id: str = None):
        
        is_collection_exists = await self.is_collection_exists(collection_name)

        if not is_collection_exists:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        if not record_id:
            self.logger.info(f"Cannot insert record without record_id. ")
            return False


        async with self.db_client as session:
            async with session.begin():
                insert_sql = sql_text(
                    f'INSERT INTO {collection_name} '
                    f'({PgVectorTableSchemaEnum.CHUNK_ID.value}, '
                    f'{PgVectorTableSchemaEnum.TEXT.value}, '
                    f'{PgVectorTableSchemaEnum.VECTOR.value}, '
                    f'{PgVectorTableSchemaEnum.METADATA.value}) '
                    f'VALUES (:chunk_id, :text, :vector, :metadata)'
                )
                
                await session.execute(insert_sql, {
                    'chunk_id': record_id,
                    'text': text,
                    'vector': "[" + ",".join([str(v) for v in vector]) + "]",
                    'metadata': metadata
                })

                await session.commit()

        return True
    
    async def insert_many(self, collection_name: str, texts: list, vectors: list,
                          metadata: list = None, record_ids: list = None, batch_size: int = 50):
        
        is_collection_exists = await self.is_collection_exists(collection_name)

        if not is_collection_exists:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        if len(vectors) != len(record_ids):
            self.logger.error("Vectors and record IDs must have the same length.")
            return False

        async with self.db_client as session:
            async with session.begin():
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    batch_vectors = vectors[i:i + batch_size]
                    batch_metadata = metadata[i:i + batch_size] 
                    batch_record_ids = record_ids[i:i + batch_size]

                    values = []

                    for _text, _vector, _metadata, _record_id in zip(
                        batch_texts, batch_vectors, batch_metadata, batch_record_ids
                    ):
                        values.append(
                            {
                                'chunk_id': _record_id,
                                'text': _text,
                                'vector': "[" + ",".join([str(v) for v in _vector]) + "]",
                                'metadata': _metadata
                            }
                        )

                    
                    batch_insert_sql = sql_text(
                        f'INSERT INTO {collection_name} '
                        f'({PgVectorTableSchemaEnum.CHUNK_ID.value}, '
                        f'{PgVectorTableSchemaEnum.TEXT.value}, '
                        f'{PgVectorTableSchemaEnum.VECTOR.value}, '
                        f'{PgVectorTableSchemaEnum.METADATA.value}) '
                        f'VALUES (:chunk_id, :text, :vector, :metadata)'
                    )

                    await session.execute(batch_insert_sql, values)

        return True
    
        
    async def search_by_vector(self, collection_name: str, vector: list, 
                        limit: int = 10) -> List[RetrievedDocuments]:

        is_collection_exists = await self.is_collection_exists(collection_name)
        
        if not is_collection_exists:
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []

        vector = "[" + ",".join([str(v) for v in vector]) + "]"

        async with self.db_client as session:
            async with session.begin():
                search_sql = sql_text(f'SELECT {PgVectorTableSchemaEnum.TEXT.value} as text, 1 - ({PgVectorTableSchemaEnum.VECTOR.value} <=> :vector) as score'
                        f' FROM {collection_name}'
                        ' ORDER BY score DESC '
                        f'LIMIT {limit}'
                        )

                result = await session.execute(search_sql, {"vector": vector})

                records = result.fetchall()

                return [
                    RetrievedDocuments(
                        text=record.text,
                        score=record.score
                    )
                    for record in records
                ]