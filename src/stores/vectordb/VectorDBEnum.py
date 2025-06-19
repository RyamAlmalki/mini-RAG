from enum import Enum

class VectorDBEnum(Enum):
    QDRANT = "qdrant"
    PGVECTOR = "pgvector"


class DistanceMethodEnum(Enum):
    COSINE = "Cosine"
    DOT = "Dot"


class PgVectorTableSchemaEnum(Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"

class PgVectorDistanceMethodEnum(Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_12_ops"
    
