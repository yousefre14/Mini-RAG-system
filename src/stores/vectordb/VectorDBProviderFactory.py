from .ProvidersDB import QdrantDB
from .VectorDBEnum import VectorDBType, DistaceMethodeEnum
from src.controllers.BaseController import BaseController
import os

class VectorDBProviderFactory:
    def __init__(self, config):
        self.config = config
        self.base_controller = BaseController()

    def create(self,provider:str):    
        if provider == VectorDBType.Qdrant.value:
            db_path = self.base_controller.get_vector_db_provider(self.config["VECTOR_DB_PATH"])

            return QdrantDB(db_path=db_path, 
                            distance_method=DistaceMethodeEnum(self.config["VECTOR_DB_DISTANCE_METHOD"]))
        return None
    