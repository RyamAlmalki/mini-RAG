from abc import ABC, abstractmethod


class LLMinterface(ABC):

    @abstractmethod
    def set_generation_model(self, model: str):
        pass

    @abstractmethod
    def set_embeddings_model(self, model: str):
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, max_output_tokens: int, 
                      temperature: float = None):
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        pass