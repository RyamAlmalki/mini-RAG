from .BaseDataModel import BaseDataModel
from .enums.DataBaseEnum import DataBaseEnum
from .db_schemes import DataChunks
from bson.objectid import ObjectId
from sqlalchemy import select, delete
from sqlalchemy.sql import func


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client)  # this will call the __init__ method
        return instance


    async def create_chunk(self, chunk: DataChunks):
        async with self.db_client() as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        
        return chunk
    

    async def get_chunk_by_id(self, chunk_id: str):
        async with self.db_client() as session:
                result = await session.execute(select(DataChunks).where(DataChunks.chunk_id == chunk_id))
                chunk = result.scalar_one_or_none()
        return chunk


    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):
        
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i + batch_size]
                    session.add_all(batch)
            await session.commit()
        
        return len(chunks)

    async def delete_chunk_by_project_id(self, project_id: ObjectId):
        async with self.db_client() as session:
            stmt = delete(DataChunks).where(DataChunks.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount
    

    async def get_project_chunks(self, project_id: ObjectId, page_number: int = 1, page_size: int = 50):
        async with self.db_client() as session:
            stmt = select(DataChunks).where(DataChunks.chunk_project_id == project_id).offset((page_number - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            chunks = result.scalars().all()
        return chunks
    
    async def get_total_chunks_count(self, project_id: ObjectId):
        async with self.db_client() as session:
            stmt = select(func.count(DataChunks)).where(DataChunks.chunk_project_id == project_id)
            result = await session.execute(stmt)
            count = result.scalar()
        return count