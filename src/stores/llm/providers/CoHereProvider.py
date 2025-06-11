from ..LLMInterface import LLMInterface
import logging 
from ..LLMEnum import CoHereEnum, DocumentTypeEnum
from cohere import Client 

class CoHereProvider(LLMInterface):
    def __init__(self, api_key: str,
                default_input_max_characters: int=1000, 
                default_generation_max_output_token: int=1000,
                defult_generation_temperature: float=0.1,
                ):
    
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_token = default_generation_max_output_token
        self.defult_generation_temperature = defult_generation_temperature
        
        self.generation_model_id = None 
        
        self.embedding_model_id = None
        self.embedding_size = None
        self.enums = CoHereEnum

        self.client = Client(api_key=self.api_key)
        
        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text):
        if isinstance(text, list):
            text = " ".join(text)
        return text[:self.default_input_max_characters].strip()
    
    def generate_text(self, prompt: str, chat_history: list=[],
        max_output_tokens: int=None, temperature: float = None):
        
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_generation_max_output_token
        temperature = temperature if temperature is not None else self.defult_generation_temperature

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            temperature=temperature,
            max_tokens=max_output_tokens
        )

        if response is None or not response.text:
            self.logger.error("Failed to generate text.")
            return None

        return response.text
    
    def embed_text(self, text: str, document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        
        input_type = CoHereEnum.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CoHereEnum.QUERY.value
        
        response = self.client.embed(
            model=self.embedding_model_id,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=['float']
        )

        logging.info(f"Embedding response: {response}")
        
        if response is None or not response.embeddings:
            self.logger.error("Failed to embed text.")
            return None
        
        return response.embeddings.float[0]


    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "message": self.process_text(prompt)
        }