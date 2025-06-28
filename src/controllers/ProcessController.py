from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from models import ProcessingEnum
from typing import List
from dataclasses import dataclass


@dataclass
class Document:
    page_content: str
    metadata: dict


class ProcessController(BaseController):
   
    def __init__(self, project_id:str):
      super().__init__()
      self.project_id = project_id
      self.project_path = ProjectController().get_project_path(project_id)

    def get_file_extension(self, file_path: str):
        return os.path.splitext(file_path)[-1]
    
    def get_file_loader(self, file_id: str):
        
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None
        
        file_extension = self.get_file_extension(file_path)
        
        if file_extension == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        elif file_extension == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None

    def get_file_content(self, file_id: str):
        loader = self.get_file_loader(file_id)

        if loader:
            documents = loader.load()
            return documents
        
        return None

    def process_file_content(self, file_contents: list, file_id: str, chunk_size: int = 100, chunk_overlap: int = 20):
        
        if file_contents is None:
            logger.error(f"No content found for file: {file_id}")
            return None

        file_contents_texts = [
            record.page_content
            for record in file_contents 
        ]
    
        file_contents_metadata = [
           record.metadata
           for record in file_contents 
        ]

        chunks = self.process_simpler_splitter(
            texts=file_contents_texts, 
            metadatas=file_contents_metadata, 
            chunk_size=chunk_size
        )

        return chunks
    

    from langchain.schema import Document  


    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict] = None, chunk_size: int = 100, splitter_tag: str = "\n"):
        full_text = " ".join(texts)

        lines = [doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag

            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(), 
                    metadata={}
                ))
                current_chunk = ""

        if current_chunk.strip():
            chunks.append(Document(
                page_content=current_chunk.strip(), 
                metadata={}
            ))

        return chunks
