from enum import Enum

class VectorDBType(Enum):
    Qdrant = "Qdrant"

class DistaceMethodeEnum(Enum):
    Cosine = "Cosine"
    Euclidean = "Euclidean"
    DotProduct = "DotProduct"