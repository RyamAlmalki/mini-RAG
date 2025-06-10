import json
from .BaseController import BaseController
from models.ProjectModel import ProjectModel
from models.ChunkModel import DataChunk
from typing import List
from stores.llm.LLMEnum import DocumentTypeEnum

class NLPController(BaseController):
    def __init__(self, vector_db_client, generation_client, embedding_client):
        super().__init__()
      
        self.vector_db_client = vector_db_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
    
    
    def create_collection_name(self, project_id: str):
        return f"collection_{self.vector_db_client.default_vector_size}_{project_id}".strip()
    

    async def reset_vector_db_collection(self, project: ProjectModel):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vector_db_client.delete_collection(collection_name=collection_name)


    async def get_vector_db_collection_info(self, project: ProjectModel):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vector_db_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )

    async def index_into_vector_db(self, project: ProjectModel, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: manage items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # step3: create collection if not exists
        _ = await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = await self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    

    

    
