from .ProvidersDB import QdrantDB
from .VectorDBEnum import VectorDBType, DistaceMethodeEnum
from controllers.BaseController import BaseController

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create_provider(self,provider:str):    
        if provider == VectorDBType.Qdrant.value:
            db_path = self.base_controller.get_vector_db_provider(self.config.vectordb_path)

            return QdrantDB(db_path=db_path, 
                            distance_method=DistaceMethodeEnum(self.config.vectordb_distance_method))
        return None
    