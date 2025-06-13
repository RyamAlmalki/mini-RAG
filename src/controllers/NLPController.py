import asyncio
import json
from .BaseController import BaseController
from models.ProjectModel import ProjectModel
from models.ChunkModel import DataChunks
from typing import List
from stores.llm.LLMEnum import DocumentTypeEnum
import time

class NLPController(BaseController):
    def __init__(self, vector_db_client, generation_client, embedding_client, template_parser):
        super().__init__()
      
        self.vector_db_client = vector_db_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser
    

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

    # async def index_into_vector_db(self, project: ProjectModel, chunks: List[DataChunks],
    #                                chunks_ids: List[int], 
    #                                do_reset: bool = False):
        
    #     # step1: get collection name
    #     collection_name = self.create_collection_name(project_id=project.project_id)

    #     # step2: manage items
    #     texts = [ c.chunk_text for c in chunks ]
    #     metadata = [ c.chunk_metadata for c in  chunks]
    #     # vectors = [
    #     #     self.embedding_client.embed_text(text=text, 
    #     #                                      document_type=DocumentTypeEnum.DOCUMENT.value)
    #     #     for text in texts
    #     # ]


    #     vectors = []
    #     for text in texts:
    #         vector = self.embedding_client.embed_text(
    #             text=text,
    #             document_type=DocumentTypeEnum.DOCUMENT.value
    #         )
    #         vectors.append(vector)
    #         time.sleep(0.7)  # ~85 calls per minute — stays under 100


    #     # step3: create collection if not exists
    #     _ = await self.vector_db_client.create_collection(
    #         collection_name=collection_name,
    #         embedding_size=self.embedding_client.embedding_size,
    #         do_reset=do_reset,
    #     )

    #     # step4: insert into vector db
    #     _ = await self.vector_db_client.insert_many(
    #         collection_name=collection_name,
    #         texts=texts,
    #         metadata=metadata,
    #         vectors=vectors,
    #         record_ids=chunks_ids,
    #     )

    #     return True

    async def index_into_vector_db(self, project: ProjectModel, chunks: List[DataChunks],
                                chunks_ids: List[int], 
                                do_reset: bool = False, batch_size: int = 50):
        
        collection_name = self.create_collection_name(project_id=project.project_id)
        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]

        vectors = []

        # Process texts in batches asynchronously
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]

            # Assume your client has an async batch embed method
            batch_vectors = await self.embedding_client.embed_texts(
                texts=batch_texts,
                document_type=DocumentTypeEnum.DOCUMENT.value
            )
            vectors.extend(batch_vectors)

            # Optional: small delay
            await asyncio.sleep(0.5)  

        # Create collection async call
        await self.vector_db_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # Insert batch into vector DB async call
        await self.vector_db_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True


    async def search_vector_db_collection(self, project: ProjectModel, text: str, limit: int = 5):
        
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step2: embed the text
        vector = self.embedding_client.embed_text(
            text=text, 
            document_type=DocumentTypeEnum.QUERY.value
        )
        
        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search
        results = await self.vector_db_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False
        

        return results



    async def answer_rag_question(self, project: ProjectModel, query: str, limit: int = 10):
        
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "document_number": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step3: Construct Generation Client Prompts
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history