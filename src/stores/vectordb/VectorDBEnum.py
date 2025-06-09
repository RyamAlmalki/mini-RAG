from enum import Enum

class VectorDBEnum(Enum):
    QDRANT = "qdrant"


class DistanceMethodEnum(Enum):
    COSINE = "Cosine"
    DOT = "Dot"