from enum import Enum

class DataBaseEnum(Enum):
    PROJECTS = "projects"
    COLLECTIONS_CHUNK_NAME = "chunks"
    DOCUMENTS = "documents"
    EMBEDDINGS = "embeddings"
    RETRIEVALS = "retrievals"