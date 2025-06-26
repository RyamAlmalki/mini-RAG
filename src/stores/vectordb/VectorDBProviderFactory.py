from .providers import QdrantDBProvider, PGVectorProvider
from helper.config import Settings
from .VectorDBEnum import VectorDBEnum
from controllers.BaseController import BaseController
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:
    
    def __init__(self, config: Settings, db_clint: sessionmaker=None):
        self.config = config
        self.base_controller = BaseController()
        self.db_clint = db_clint

    async def create(self, provider: str):
        if provider == VectorDBEnum.QDRANT.value:
            qdrant_db_clint = self.base_controller.get_database_path(database_name=self.config.VECTOR_DB_PATH)
            
            return QdrantDBProvider(
                db_client=qdrant_db_clint,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECOTR_DB_PGVECTOR_INDEX_THRESHOLD
            )
        elif provider == VectorDBEnum.PGVECTOR.value:
            return PGVectorProvider(
                db_client=self.db_clint,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.EMBEDDING_MODEL_SIZE,
                index_threshold=self.config.VECOTR_DB_PGVECTOR_INDEX_THRESHOLD,
            )



        return None
    

